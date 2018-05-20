FROM python:3-stretch AS build
LABEL maintainer="norbert@not7cd.net"

RUN pip3 install pipenv

COPY Pipfile Pipfile.lock /tmp/
ENV PIPENV_PIPFILE /tmp/Pipfile
RUN pipenv install --deploy --system

WORKDIR /app
COPY . .

#default config
ENV SECRET_KEY secret
ENV PYTHONPATH /app
ENV DB_PATH /data/whoisdevices.db

RUN mkdir /data && chown nobody /data
VOLUME ["/data"]

USER nobody
EXPOSE 8000
CMD ["gunicorn", "whois.web:app", "-b 0.0.0.0:8000"]
