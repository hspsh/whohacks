# Whois @ HS3C

Aplikacja zbierająca dane o aktualnie podłączonych użytkownikach do sieci.

Przy 500 linijkach można rozważyć rozbicie na pliki

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

## Produkcja
```
gunicorn whois.web:app
```
