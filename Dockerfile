FROM python:3

COPY . .
WORKDIR .

RUN pip install pipenv
RUN pipenv install --system

ENV SECRET_KEY dev-key
VOLUME whoisdevices.db
CMD ["python", "helpers/db_create.py"]

CMD ["python", "-m", "whois"]