# Django Project
***Office of the Registrator***

For Windows
* `python -m venv venv`
* `venv\Scripts\activate`
* `python -m pip install --upgrade pip`
* `pip install -r requirements.txt`
* You need to install `postgresql`
* Create new database `office`, changing `DATABASES` in `settings.py` by using your data


 You can use `dump.sql` file to restore sample **DB** \
`https://o7planning.org/ru/11913/backup-and-restore-postgres-database-with-pgadmin#a33893371` \
 Or you must delete `migration` files to create new DataBase