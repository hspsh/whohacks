FROM python:3-buster AS build
LABEL maintainer="norbert@not7cd.net"

ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN pip3 install poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml /app/
COPY poetry.lock /app/

WORKDIR /app
RUN poetry install --no-dev
COPY . .

#default config
ENV SECRET_KEY S3cret

RUN mkdir /data && chown nobody /data
VOLUME ["/data"]

USER nobody
EXPOSE 8000
CMD ["gunicorn", "whois.web:app", "-b 0.0.0.0:8000"]
