#! /bin/bash

rm -f db.sqlite3

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --username=dev --email=dev@dev.com
python manage.py runserver
