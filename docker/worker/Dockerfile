FROM python:3-buster AS build
LABEL maintainer="norbert@not7cd.net"

ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN pip3 install poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock /app/ 

WORKDIR /app
RUN poetry install --no-dev
COPY . .

#default config
ENV PYTHONPATH /app
ENV DB_PATH /data/whoisdevices.db
ENV MQ_HOST localhost
ENV MQ_EXCHANGE whohacks

RUN mkdir /data && chown nobody /data
VOLUME ["/data"]

USER nobody
EXPOSE 8000
CMD ["python", "whois/worker.py"]
