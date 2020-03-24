FROM python:3.7.2-alpine

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install -r requirements.txt
RUN pip install gunicorn psycopg2

COPY flaskapp flaskapp
COPY config.py manage.py ./
RUN chmod +x boot.sh

ENV FLASK_APP manage.py

RUN CHMOD
ENTRYPOINT ['./boot.sh']