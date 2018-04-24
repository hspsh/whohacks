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
docker run -v whois-db:/data -p 5000:5000 whois:latest
```
### Docker compose

`docker-compose up`

### Envvars

`SECRET_KEY`

### Finding the database contents

Look for mountpoint via `docker inspect whois-db`

If you'd like to migrate from a previously running instance please copy the contents of db into current Docker volume
