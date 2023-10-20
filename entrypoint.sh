#!/usr/bin/env bash

python manage.py collectstatic  --no-input --clear
python manage.py migrate --noinput
gunicorn --config gunicorn_config.py wordtrack.wsgi:application
