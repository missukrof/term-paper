from math import floor

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["figure.figsize"] = (20, 10)
plt.style.use("fivethirtyeight")


def get_bb(data, window, std):
    sma = data.rolling(window=window).mean()
    std = data.rolling(window=window).std(std)
    upper_bb = sma + std * 2
    lower_bb = sma - std * 2
    result = pd.concat([sma, upper_bb, lower_bb], axis=1)
    result.columns = [f"sma_{window}", "upper_bb", "lower_bb"]

    return result


def implement_bb_strategy(data, lower_bb, upper_bb):
    buy_price = []
    sell_price = []
    bb_signal = []
    signal = 0

    for i in range(len(data)):
        if data[i - 1] > lower_bb[i - 1] and data[i] < lower_bb[i]:
            if signal != 1:
                buy_price.append(data[i])
                sell_price.append(np.nan)
                signal = 1
                bb_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_signal.append(0)
        elif data[i - 1] < upper_bb[i - 1] and data[i] > upper_bb[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(data[i])
                signal = -1
                bb_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            bb_signal.append(0)

    return buy_price, sell_price, bb_signal


def plot_signals_bb(df_price, bb_df, buy_price, sell_price):
    df_price["close"].plot(label="CLOSE PRICES", alpha=0.3)
    bb_df["upper_bb"].plot(label="UPPER BB", linestyle="--", linewidth=1, color="black")
    bb_df[[col for col in bb_df.columns.to_list() if col.find("sma_") > -1][0]].plot(
        label="MIDDLE BB", linestyle="--", linewidth=1.2, color="grey"
    )
    bb_df["lower_bb"].plot(label="LOWER BB", linestyle="--", linewidth=1, color="black")
    plt.scatter(
        df_price.index, buy_price, marker="^", color="green", label="BUY", s=200
    )
    plt.scatter(
        df_price.index, sell_price, marker="v", color="red", label="SELL", s=200
    )
    plt.title("ETHUSDT BB SIGNALS")
    plt.legend(loc="upper left")
    plt.show()


def get_best_params_bb(df_price, window, std, investment_value):
    ethusdt_bb = get_bb(df_price["close"], window, std)
    buy_price, sell_price, bb_signal = implement_bb_strategy(
        df_price["close"], ethusdt_bb["lower_bb"], ethusdt_bb["upper_bb"]
    )

    position = []
    for i in range(len(bb_signal)):
        if bb_signal[i] > 1:
            position.append(0)
        else:
            position.append(1)

    for i in range(len(df_price["close"])):
        if bb_signal[i] == 1:
            position[i] = 1
        elif bb_signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i - 1]

    upper_bb = ethusdt_bb["upper_bb"]
    lower_bb = ethusdt_bb["lower_bb"]
    close_price = df_price["close"]
    bb_signal = (
        pd.DataFrame(bb_signal)
        .rename(columns={0: "bb_signal"})
        .set_index(df_price.index)
    )
    position = (
        pd.DataFrame(position)
        .rename(columns={0: "bb_position"})
        .set_index(df_price.index)
    )

    frames = [close_price, upper_bb, lower_bb, bb_signal, position]
    strategy = pd.concat(frames, axis=1)
    strategy = strategy.reset_index(drop=True)

    bb_ret = pd.DataFrame(np.diff(df_price["close"])).rename(columns={0: "returns"})
    bb_strategy_ret = []

    for i in range(len(bb_ret)):
        try:
            returns = bb_ret["returns"][i] * strategy["bb_position"][i]
            bb_strategy_ret.append(returns)
        except:
            pass

    bb_strategy_ret_df = pd.DataFrame(bb_strategy_ret).rename(columns={0: "bb_returns"})

    number_of_stocks = floor(investment_value / df_price["close"][0])
    bb_investment_ret = []

    for i in range(len(bb_strategy_ret_df["bb_returns"])):
        returns = number_of_stocks * bb_strategy_ret_df["bb_returns"][i]
        bb_investment_ret.append(returns)

    bb_investment_ret_df = pd.DataFrame(bb_investment_ret).rename(
        columns={0: "investment_returns"}
    )
    total_investment_ret = round(sum(bb_investment_ret_df["investment_returns"]), 2)
    profit_percentage = floor((total_investment_ret / investment_value) * 100)

    return total_investment_ret, profit_percentage
