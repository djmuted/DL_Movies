FROM python:3.9.5-slim
COPY . /app
WORKDIR /app
RUN apt-get update
RUN apt-get install -y nginx build-essential libpq-dev
RUN pip install -r requirements.txt
COPY ./docker/nginx.conf /etc/nginx/sites-available/default
RUN python manage.py collectstatic
RUN chmod -R 755 /app
EXPOSE 80
ENTRYPOINT ["/bin/sh", "-c" , "/app/docker/run.sh"]