FROM python:3-stretch
MAINTAINER not7cd "norbert@not7cd.net"

COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

COPY . /service/app
WORKDIR /service

ENV SECRET_KEY dev-key
ENV PYTHONPATH /service/app
ENV DB_PATH /data/whoisdevices.db

RUN pip3 install gunicorn

EXPOSE 8000
CMD gunicorn whois.web:app -b 0.0.0.0:8000

