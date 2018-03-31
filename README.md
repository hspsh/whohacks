# whois @ HS3C


## Instalacja
Używam tutaj pipenv'a 
```bash
pipenv install
```
Pierwsze uruchomienie
```bash
pipenv run python helpers/db_create.py
```
Uruchamianie
```bash
pipenv run python -m whois
```

## Stawianie dockera
_Bo mamy za mało problemów_
```bash
docker volume create --name whois-db
docker build . -t 'whois'
docker run -v whois-db:/data -p 5000:5000 whois:latest python3 helpers/db_create.py
docker run -v whois-db:/data -p 5000:5000 whois:latest
```
To rozwiązanie tworzy folder z bazą danych która jest zachowana między instancjami kontenerów.
Aby znaleźć folder z zachowaną bazą należy poszukać mountpoint w ```docker inspect whois-db```
Wypada zmienić SECRET_KEY.