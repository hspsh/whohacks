FROM python:3-stretch AS builder
LABEL maintainer="norbert@not7cd.net"

RUN pip3 install wheel pipenv_to_requirements

WORKDIR /app

RUN mkdir /data && chown nobody /data

COPY Pipfile Pipfile.lock ./

RUN pipenv_to_requirements -f
RUN pip install wheel && pip wheel -r requirements.txt --wheel-dir=/app/wheels

COPY . .


FROM python:3-stretch

COPY --from=builder /app /app
WORKDIR /app
RUN pip install --no-index --find-links=/app/wheels -r requirements.txt

#default config
ENV SECRET_KEY secret
ENV PYTHONPATH /app
ENV DB_PATH /data/whoisdevices.db

USER nobody
EXPOSE 8000
CMD ["gunicorn", "whois.web:app", "-b 0.0.0.0:8000"]
