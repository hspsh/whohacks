# Whois @ HS3C

Aplikacja zbierająca dane o aktualnie podłączonych użytkownikach do sieci.

Przy 500 linijkach można rozważyć rozbicie na pliki

## Produkcja
```
gunicorn whois.web:app
```
