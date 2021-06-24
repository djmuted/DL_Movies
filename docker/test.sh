#!/bin/sh
cd /app
python -u manage.py migrate && \
python manage.py test