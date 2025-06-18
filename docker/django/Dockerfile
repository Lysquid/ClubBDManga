# syntax=docker/dockerfile:1
FROM python:3.13
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY docker/django/requirements.txt /app/prod-requirements.txt
RUN pip install -r prod-requirements.txt

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

CMD ./docker/django/entrypoint.sh
