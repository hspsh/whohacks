FROM kennethreitz/pipenv
MAINTAINER not7cd "norbert@not7cd.net"

COPY . /app

ENV SECRET_KEY dev-key
ENV PYTHONPATH=/app
ENV DB_PATH=/data/whoisdevices.db

CMD python3 -m whois