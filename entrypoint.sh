#!/usr/bin/env bash

python manage.py collectstatic  --no-input --clear
python manage.py migrate --noinput
gunicorn --bind 0.0.0.0:8000 wordtrack.wsgi:application
