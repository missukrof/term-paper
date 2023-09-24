## Term paper project
### 📁Folder structure
Data capture:
* [Configs](https://github.com/missukrof/term-paper/tree/main/configs): config/settings files;
* [MySQL_DB](https://github.com/missukrof/term-paper/tree/main/mysql_db): mysql client for database manipulation;
* [SQL](https://github.com/missukrof/term-paper/tree/main/sql): SQL scripts for working with a database.
* [Research](https://github.com/missukrof/term-paper/tree/main/research): main project research.
### 💻Execution of the data collection part of the project
Setting the environment with all requirements using poetry:
```cli
python -m venv venv
pip install virtualenv
./venv/Scripts/activate
pip install poetry
poetry install
```
Make sure you have created .env file (place in in root of the project) with credentials for the MySQL DB:
```env
# MySQL credentials
DB_HOST = "host"
DB_DATABASE = "database"
DB_LOGIN = "login"
DB_PASSWORD = "password"
```
Specifying settings for data collection in [data_collection.toml](https://github.com/missukrof/term-paper/blob/main/configs/data_collection.toml):
```toml
[SPOT_1H] # Name of the data collection specification
symbol="ETHUSDT" # Data ticket
start_time="2020-01-01" # Start date
end_time="2023-01-01" # End date
active="SPOT" # Active
interval="1h" # Interval
```
Executing file to run data capture: [collect_data.py](https://github.com/missukrof/term-paper/blob/main/collect_data.py).
Run it in cli:
```cli
python collect_data.py get_all_data
```
