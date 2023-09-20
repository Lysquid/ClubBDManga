# syntax=docker/dockerfile:1
FROM python:3.11
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install gunicorn
RUN pip install -r requirements.txt

COPY . /app/

CMD ./docker/django/entrypoint.sh
