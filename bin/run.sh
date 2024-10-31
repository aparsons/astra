#! /bin/bash

# This script sets up a Python project using Poetry, installs dependencies, and runs the Django development server.


poetry install

poetry shell

python manage.py createsuperuser --username=dev --email=dev@dev.com --noinput
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
