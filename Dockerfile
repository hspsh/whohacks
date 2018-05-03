FROM kennethreitz/pipenv

#TODO: delete it, an require setup
ENV SECRET_KEY devkey
ENV PYTHONPATH /app
ENV DB_PATH /data/whoisdevices.db

COPY . /app

RUN mkdir /data && chown nobody:nogroup /data

EXPOSE 8000
USER nobody
CMD ["gunicorn", "whois.web:app", "-b 0.0.0.0:8000"]
