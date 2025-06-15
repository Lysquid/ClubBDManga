# syntax=docker/dockerfile:1
FROM python:3.13
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install "gunicorn>=23.0.0,<24.0"
RUN pip install -r requirements.txt

COPY . /app/

CMD ./docker/django/entrypoint.sh
