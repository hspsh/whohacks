# whohacks @ hsp.sh?

[![Build status](https://github.com/hspsh/whohacks/actions/workflows/build.yml/badge.svg)](https://github.com/hspsh/whohacks/actions/workflows/build.yml) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Prerequisities

- poetry

## Instalation

### Install dependencies

```shell
poetry install
```

## Setup whohacks locally

### Create the database

Local setup involves using the sqlite3 database. Before running the web server,
we need to create the database with helper script:

```shell
poetry run python helpers/db_create.py
```

### Setup Environment Variables

Set the following environment variables:

1. `SECRET_KEY`
2. `APP_IP_MASK` - A mask that filters the allowed IP's, allowing blocking
   requests outside of the accepted network. For the local development purposes
   this can be set to `127.0.0.1` to allow requests only from the host machine.

Example of setting environemnt variables:

- Windows: `set SECRET_KEY=example123`.

- Linux: `export SECRET_KEY=example123`.

### Launch the web server

```shell
poetry run python -m whois
```

You can access the webpage by the `localhost:5000` (default settings).

## Setup via Docker

- Create .env file, buy it doesn't work. Go figure

```shell
source env.sh
```

### Create the database

```shell
docker compose run web python helpers/db_create.py
```

### Deploy via docker-compose

```shell
docker compose up
```

## OAuth2 integration

see: https://github.com/navikt/mock-oauth2-server

configuration can be found in ./tests/resources

If you want for redirects to work properly you need to add mock oauth to `/etc/hosts`

```bash
echo "127.0.0.1 oauth.localhost" >> /etc/hosts
```

But if you can't, you can always change `oauth.localhost` to `localhost` in your browser when redirect fails.

## Deployment

```shell
docker-compose build
# first run, later it should just connect to existing db
docker-compose run web python3 helpers/db_create.py
docker-compose up
```

## Testing

You can run the tests with `poetry run python -m unittest`

### Caution

This: `-v /etc/localtime:/etc/localtime:ro` is required to match the timezone in the container to timezone of the host

### Docker compose

Sample:

```yaml
version: "3"
services:
  rabbitmq:
    image: "rabbitmq:3.6-management-alpine"
    ports:
      - "5672:5672"
      - "15672:15672"
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
