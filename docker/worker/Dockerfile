FROM python:3-stretch AS build
LABEL maintainer="norbert@not7cd.net"

RUN pip3 install pipenv

COPY Pipfile Pipfile.lock /tmp/
ENV PIPENV_PIPFILE /tmp/Pipfile
RUN pipenv install --deploy --system

WORKDIR /app
COPY . .

#default config
ENV PYTHONPATH /app
ENV DB_PATH /data/whoisdevices.db
ENV MQ_HOST localhost
ENV DB_EXCHANGE whohacks

RUN mkdir /data && chown nobody /data
VOLUME ["/data"]

USER nobody
EXPOSE 8000
CMD ["python", "whois/worker.py"]
