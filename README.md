# WebMark

[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.png?v=103)](https://opensource.org/licenses/mit-license.php)

Web platform for benchmarking quantum computing algorithms

## Django - structure

WebMark = Project

WebCLI = Application

Requirements: django, django-on-heroku, gunicorn

## Setting up the development environment

Install PostgreSQL:

```
sudo apt-get install postgresql postgresql-contrib libpq-dev python3-dev
```

Create a database:
```
sudo -u postgres psql
postgres=# create database kvanttidb;
postgres=# create user kvanttiuser with encrypted password 'secret';
postgres=# grant all privileges on database kvanttidb to kvanttiuser;
postgres=# \q
```

Create a .env file in the project root with the following contents:
```
DATABASE_NAME=kvanttidb
DATABASE_USER=kvanttiuser
DATABASE_PASSWORD=secret
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
```

Create and activate a virtual enviroment:
```
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:
```
pip install -r requirements.txt
```

Now you can run the development server with command:
```
python manage.py runserver
```

How to push local postgre database to heroku
```
heroku pg:push postgres://kvanttiuser@localhost/kvanttidb  postgresql-flexible-07270 --app=quantmark
```


