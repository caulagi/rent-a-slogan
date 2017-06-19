# rent-a-slogan

A highly performant, evented, system for renting slogans!

    * Clients can add a slogan
    * Clients can rent a slogan for 15 seconds
    * Clients can ask for status of rental system

## Setup

The recommended python version is **3.6.x**. If you don't have Python3.6 locally,
try the docker version below.

### Running locally

```
$ docker volume create rent-slogan
$ docker run \
    -v rent-slogan:/var/lib/postgresql/data \
    -e POSTGRES_PASSWORD=1234 \
    -e POSTGRES_DB=rent-slogan \
    -p 5432:5432 \
    -d postgres:9.6-alpine

$ python3 -m venv ~/.venv/ras
$ source ~/.venv/ras/bin/activate

$ python server.py
```

## Design

TODO

## Tests

TODO
