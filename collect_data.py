import os
from datetime import datetime as dt
from datetime import timedelta

import fire
import numpy as np
import requests
from dotenv import load_dotenv

from configs.config import logging, settings
from mysql_db.client import MySQLClient


class GetData:
    def __init__(self):
        self.settings_args = settings.as_dict()

    def get_data_binance(
        self,
        symbol,
        start_time: str,
        end_time: str,
        active: str,
        interval: str = None,
    ):
        load_dotenv()

        start_time_ms = int(dt.strptime(start_time, "%Y-%m-%d").timestamp()) * 1000
        end_time_ms = int(dt.strptime(end_time, "%Y-%m-%d").timestamp()) * 1000

        logging.info(
            f"Defining a script to create a {symbol} {active} "
            + f"{interval + ' ' if interval is not None else ''}table..."
        )

        if active.lower() == "fundrates":
            sql_file = "sql/create_tables_fundrates.sql"
        else:
            sql_file = "sql/create_tables_tr.sql"

        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time_ms,
            "endTime": end_time_ms,
            "limit": 500,
        }

        with open(sql_file, "r") as f:
            create_table_q = f.read()

        create_table_q = create_table_q.format(
            database=os.getenv("DB_DATABASE"),
            symbol=params["symbol"],
            active=active,
            interval=f"_{params['interval']}" if params["interval"] is not None else "",
        )

        logging.info(
            f"A script to create a {symbol} {active} "
            + f"{interval + ' ' if interval is not None else ''}is defined:\n{create_table_q}"
        )
        logging.info(
            f"Execution of the script to create a {symbol} {active} "
            + f"{interval + ' ' if interval is not None else ''}table..."
        )

        client = MySQLClient()
        client.execute_query(create_table_q)

        logging.info(
            f"Table {symbol} {active} "
            + f"{interval + ' ' if interval is not None else ''}is created."
        )

        logging.info(
            f"Filling in the {symbol} {active} "
            + f"{interval + ' ' if interval is not None else ''}table..."
        )
        while True:
            if active.lower() == "fundrates":
                check_end_time_ms = dt.fromtimestamp(end_time_ms / 1000) + timedelta(
                    hours=8, seconds=1
                )
                params["endTime"] = int(check_end_time_ms.timestamp()) * 1000
                try:

                    with open("sql/insert_values.sql", "r") as f:
                        insert_values_q = f.read()

                    response = requests.get(
                        "https://fapi.binance.com/fapi/v1/fundingRate", params=params
                    )
                    response = response.json()

                    timestamps = np.array([resp["fundingTime"] for resp in response])
                    start_time_ms = int(timestamps[-1])
                    params["startTime"] = start_time_ms
                    timestamps = np.array(
                        [
                            '"'
                            + dt.fromtimestamp(int(ts) / 1000).strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                            + '"'
                            for ts in timestamps
                        ]
                    ).T

                    values = np.array(
                        [
                            [resp["fundingRate"], '"' + resp["symbol"] + '"']
                            for resp in response
                        ]
                    )
                    all_vals = [
                        "({}, {})".format(i[0], ", ".join(i[1]))
                        for i in list(zip(timestamps, values))
                    ]

                    insert_values_q = insert_values_q.format(
                        database=os.getenv("DB_DATABASE"),
                        symbol=params["symbol"],
                        active=active,
                        interval=f"_{params['interval']}"
                        if params["interval"] is not None
                        else "",
                        values=", ".join(all_vals),
                    )
                    client.execute_query(query=insert_values_q)

                    check_start_time_ms = dt.fromtimestamp(
                        start_time_ms / 1000
                    ) + timedelta(hours=8, seconds=1)
                    check_start_time_ms = int(check_start_time_ms.timestamp()) * 1000

                    if check_start_time_ms > params["endTime"]:
                        logging.info(
                            f"Table {symbol} {active} "
                            + f"{interval + ' ' if interval is not None else ''}is filled.\n"
                            + "Check it by query:\n"
                            + "SELECT *\n"
                            + f"FROM {os.getenv('DB_DATABASE')}.{symbol}_{active}"
                            + f"{'_' + interval if interval is not None else ''}\n"
                            + "LIMIT 5;"
                        )
                        break

                except:
                    break
            else:
                try:
                    
                    with open("sql/insert_values.sql", "r") as f:
                        insert_values_q = f.read()
                    
                    if active.lower() == "futures":
                        response = requests.get(
                            "https://fapi.binance.com/fapi/v1/klines", params=params
                        )
                    else:
                        response = requests.get(
                            "https://api.binance.com/api/v3/klines", params=params
                        )
                    response = response.json()

                    timestamps = np.array(response)[:, 0].T
                    start_time_ms = int(timestamps[-1])
                    params["startTime"] = start_time_ms
                    timestamps = np.array(
                        [
                            '"'
                            + dt.fromtimestamp(int(ts) / 1000).strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                            + '"'
                            for ts in timestamps
                        ]
                    ).T

                    values = np.array(response)[:, 1:6]

                    all_vals = [
                        "({}, {})".format(i[0], ", ".join(i[1]))
                        for i in list(zip(timestamps, values.tolist()))
                    ]

                    insert_values_q = insert_values_q.format(
                        database=os.getenv("DB_DATABASE"),
                        symbol=params["symbol"],
                        active=active,
                        interval=f"_{params['interval']}",
                        values=", ".join(all_vals),
                    )
                    client.execute_query(query=insert_values_q)

                    if start_time_ms == end_time_ms:
                        logging.info(
                            f"Table {symbol} {active} "
                            + f"{interval + ' ' if interval is not None else ''}is filled.\n"
                            + "Check it by query:\n"
                            + "SELECT *\n"
                            + f"FROM {os.getenv('DB_DATABASE')}.{symbol}_{active}"
                            + f"{'_' + interval if interval is not None else ''}\n"
                            + "LIMIT 5;"
                        )
                        break

                except:
                    break

    def get_all_data(self):
        for config, values in self.settings_args.items():
            logging.info(f"Executing {config} with parameters: {values}...")
            self.get_data_binance(**values)


if __name__ == "__main__":
    fire.Fire(GetData)

# get_data_binance(symbol="ETHUSDT", interval="1h", start_time="2020-01-01", end_time="2020-01-03", active="SPOT")
# get_data_binance(symbol="ETHUSDT", interval="1h", start_time="2020-01-01", end_time="2020-01-03", active="FUTURES")
# get_data_binance(symbol="ETHUSDT", start_time="2020-01-01", end_time="2020-01-03", active="FUNDRATES")
