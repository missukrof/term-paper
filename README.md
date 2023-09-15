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
pip install virtualenv
python -m venv venv
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
Executing file to run data capture: [collect_data.py](https://github.com/missukrof/term-paper/blob/main/collect_data.py).
Run it in cli:
```cli
python collect_data.py get_all_data
```
