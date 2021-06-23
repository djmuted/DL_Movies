#!/bin/sh
cd /app
python -u manage.py migrate && \
python -u manage.py populate && \
nginx && \
uwsgi --master --socket /app/uwsgi.sock --chmod-socket=777 --module movies.wsgi