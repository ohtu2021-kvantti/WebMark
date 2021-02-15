# WebMark

![Python package](https://github.com/ohtu2021-kvantti/WebMark/workflows/Python%20package/badge.svg)
[![codecov](https://codecov.io/gh/ohtu2021-kvantti/WebMark/branch/main/graph/badge.svg?token=40N85S73PK)](https://codecov.io/gh/ohtu2021-kvantti/WebMark)

Web platform for benchmarking quantum computing algorithms

## Django - structure

WebMark = Project

WebCLI = Application

Requirements: django, django-on-heroku, gunicorn, django-dotenv, flake8, flake8-django

## Setting up the development environment

Install PostgreSQL:

```
sudo apt install postgresql postgresql-contrib libpq-dev python3-dev
```

Create a database:
```
sudo -u postgres psql
postgres=# create database quantdb;
postgres=# create user quantuser with encrypted password 'secret';
postgres=# grant all privileges on database quantdb to quantuser;
postgres=# alter user quantuser createdb; --allow user to create a test database
postgres=# \q
```

Create a .env file in the project root with the following contents:
```
DATABASE_NAME=quantdb
DATABASE_USER=quantuser
DATABASE_PASSWORD=secret
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
```

Create and activate a virtual environment:
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

If you get an error message when running the server, for example "psycopg2.errors.UndefinedTable: relation "WebCLI_algorithm" does not exist" you can try making migrations
```
python manage.py makemigrations WebCLI
python manage.py migrate
```
And then run the development server again.

### Setting up the development environment using Docker (alternative)

Install [Docker](https://docs.docker.com/engine/install/) according to the instructions.

Navigate to the project root and run the development server with command:
```
sudo docker-compose up
```
If any new dependancies are added f.ex. to the requirements.txt start docker with
```
sudo docker-compose up --build
```
Furthermore all the next commands can be used from Docker by 
```
sudo docker-compose run web <command_name_with_possible_parameters>
```
for example:
```
sudo docker-compose run web python manage.py makemigration
```

## Other commands

Lint your code with
```
flake8
```

Run tests
```
python manage.py test
```

Update database after change in models
```
python manage.py makemigrations
python manage.py migrate

```

You can push your local PostgreSQL database to Heroku with
```
heroku pg:push postgres://quantuser@localhost/quantdb  postgresql-flexible-07270 --app=quantmark
```


