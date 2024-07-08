# whohacks @ hsp.sh?
[![Build Status](https://travis-ci.com/hs3city/whois.svg?branch=master)](https://travis-ci.com/hs3city/whois) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Prerequisities

- poetry

## Instalation

- Dependencies

```shell
poetry install
```

- Create .env file, buy it doesn't work. Go figure

```shell
source env.sh
```

- Create database

```shell
poetry run python helpers/db_create.py
# or
poetry run init-db
```

## Running

```shell
poetry run python -m whois
```

## Deployment

```shell
docker-compose build
# first run, later it should just connect to existing db
docker-compose run web python3 helpers/db_create.py
docker-compose up
```

### Caution

This: `-v /etc/localtime:/etc/localtime:ro` is required to match the timezone in the container to timezone of the host

### Docker compose

Sample:

```yaml
version: '3'
services:
  rabbitmq:
    image: 'rabbitmq:3.6-management-alpine'
    ports:
      - '5672:5672'
      - '15672:15672'
  web:
    build: ./docker/web
    environment:
      # you should change secret key
      - SECRET_KEY=<your_secret_key>
      - DB_PATH=/data/whoisdevices.db
    ports:
      # use 127.0.0.1:8000:8000
      - "8000:8000"
    volumes:
      - database:/data
      - /etc/localtime:/etc/localtime:ro
    restart: always
  worker:
    build: ./docker/worker
    environment:
      - DB_PATH=/data/whoisdevices.db
    volumes:
      - database:/data
      - /etc/localtime:/etc/localtime:ro
    restart: always

volumes:
  database:

```

### Envvars

[`SECRET_KEY`](https://stackoverflow.com/questions/22463939/demystify-flask-app-secret-key#22463969) in .env

### Finding the database contents

Look for mountpoint via `docker inspect whois_db`

If you'd like to migrate from a previously running instance please copy the contents of db into current Docker volume
