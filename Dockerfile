FROM python:3-stretch AS build
MAINTAINER not7cd "norbert@not7cd.net"
MAINTAINER allgreed "olgierd@kasprowicz.pro"

RUN pip3 install gunicorn==19.7.1 --no-cache-dir 

COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt --no-cache-dir 
COPY . /service/app

ENV PYTHONPATH /service/app
ENV DB_PATH /data/whoisdevices.db

WORKDIR /service
EXPOSE 8000
CMD gunicorn whois.web:app -b 0.0.0.0:8000
