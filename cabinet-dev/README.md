# Muneen
This service will keep track of all the payment related queries and data.

## Abstract
This is a docker containerised project. Project is base of fastapi + sqlalchemy.
Below is the tech stack we are using:
- Python 3.8 
- FastAPI 0.78
- SqlAlchemy 
- PostgresSQL 
- SQLAdmin (FastAPI admin for sqlalchemy)
- Docker 
- AS-GI application server (probably Gunicorn)
- Alembic (Migration manager)

## Per Requirements
``Docker`` you can take reference from https://docs.docker.com/engine/install/

## Steps to set up

Clone repo on your system using below link

``
git clone git@gitlab.renewbuy.in:sleep/muneem.git
``

update postgres credentials accordingly in ``.env`` file to root directory.
 
### Sample .env file
```
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DATABASE=muneem
POSTGRES_USERNAME=renewbuy 
POSTGRES_PASSWORD=Renew2022
```

for testing, you can build docker ``docker-compose build`` and after building docker run the docker using command ``docker-compose up``

### API Contracts
You can go to the URLs at ``/openapi.json``, ``/docs``, or ``/redoc`` for api swagger.