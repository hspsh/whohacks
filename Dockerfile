FROM python:3

COPY ./requirements.txt .

COPY . .
WORKDIR .

RUN pip install --no-cache-dir -r requirements.txt
ENV SECRET_KEY chuj
CMD ["python", "helpers/db_create.py"]
CMD ["python", "-m", "whois"]