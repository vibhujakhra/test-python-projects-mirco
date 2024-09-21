# Documentic

Documentic is generator house for policy pdf.

## Abstract

This is a docker containerised project. This will help us to create policy pdf. Project is base of fastapi +
sqlalchemy + kafka.
Below is the tech stack we are using:

- Python 3.8
- FastAPI 0.78
- SqlAlchemy
- PostgresSQL
- SQLAdmin (FastAPI admin for sqlalchemy)
- Docker
- AS-GI application server (probably Gunicorn)
- Kafka

## Per Requirements

``Docker`` you can take reference from https://docs.docker.com/engine/install/

## Steps to set up

Clone repo on your system using below link

``
git clone git@gitlab.renewbuy.in:sleep/documentic.git
``

update postgres credentials accordingly in below-mentioned file

- ./settings.py

add ``.env`` file to root directory. take reference from below sample file

### .env

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=renewbuy
POSTGRES_USERNAME=renewbuy
POSTGRES_PASSWORD=renewbuy123
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=policy_generation_data
MOTOR_POLICY_DOWNLOAD_URL=http://localhost:8000/api/v1/motor/download/policy/{}
CLEVERBRIDGE_ENDPOINT=http://localhost:8000/api/v1/get-detailed-transaction/{}
DOWNLOAD_URL=http://localhost:8000/get_document/{}
BUCKET_NAME=sleep-dev
```

for testing, you can build docker ``docker-compose build`` and after building docker run the docker using
command ``docker-compose up``
