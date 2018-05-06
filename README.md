# whois @ HS3C
[![Build Status](https://travis-ci.com/hs3city/whois.svg?branch=master)](https://travis-ci.com/hs3city/whois)

## Prerequisities

- Pipenv

## Instalation

- Dependencies

```bash
pipenv install
```

- Create database

```bash
pipenv run python helpers/db_create.py
```

## Running

```bash
pipenv run python -m whois
```

## Deployment

```bash
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
version: '2'
services:
  web:
    build: .
    environment:
      # you should change secret key
      - SECRET_KEY=secret
      - DB_PATH=/data/whoisdevices.db
    ports:
      # use 127.0.0.1:8000:8000
      - "8000:8000"
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
