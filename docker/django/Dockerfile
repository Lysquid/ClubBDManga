# syntax=docker/dockerfile:1
FROM python:3.13
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml /app/
RUN pip install .[prod]

COPY . /app/

CMD ./docker/django/entrypoint.sh
