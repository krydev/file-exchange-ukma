FROM python:3.7.2-alpine

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install -r requirements.txt
RUN pip install gunicorn psycopg2

COPY flaskapp flaskapp
COPY config.py manage.py worker.py ./

ENV FLASK_APP manage.py

CMD gunicorn -b 0.0.0.0:$PORT --access-logfile - --error-logfile - manage:app