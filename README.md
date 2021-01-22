# WebMark

[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.png?v=103)](https://opensource.org/licenses/mit-license.php)

Web platform for benchmarking quantum computing algorithms

## Django - structure

WebMark = Project

WebCLI = Application

Requirements: django, django-on-heroku, gunicorn

## Installation

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
