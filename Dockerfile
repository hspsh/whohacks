FROM python:3
MAINTAINER not7cd "norbert@not7cd.net"

COPY . /app
WORKDIR /app

RUN pip install pipenv
RUN pipenv install --system

ENV SECRET_KEY dev-key
ENV PYTHONPATH=$PYTHONPATH:/app

VOLUME whoisdevices.db
RUN python helpers/db_create.py

ENTRYPOINT ["python"]
CMD ["-m", "whois"]