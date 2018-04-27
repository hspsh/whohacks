# whois @ HS3C

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

_ Because why not _

```bash
docker volume create --name whois-db
docker build . -t 'whois'
docker run -v whois-db:/data -p 5000:5000 whois:latest python3 helpers/db_create.py
docker run -v whois-db:/data -v /etc/localtime:/etc/localtime:ro -p 5000:5000 whois:latest
```

### Caution

This: `-v /etc/localtime:/etc/localtime:ro` is required to match the timezone in the container to timezone of the host

### Docker compose

Sample:

```yaml
version: '2'
services:
  whois-web:
    image: allgreed/whois
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - whois-db:/data
    # sync timezone with host
      - /etc/localtime:/etc/localtime:ro

volumes:
  whois-db:
```

### Envvars

`SECRET_KEY` in .env

### Finding the database contents

Look for mountpoint via `docker inspect whois-db`

If you'd like to migrate from a previously running instance please copy the contents of db into current Docker volume
