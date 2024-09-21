# Boiler-Plate
This will serve as a base for all FastAPI related projects going forward.

## Abstract
This is a docker containerised project. This will help us to create a base for any app we are going to design further. Project is base of fastapi + sqlalchemy.
Below is the tech stack we are using:
- Python 3.8 
- FastAPI 0.78
- SqlAlchemy 
- PostgresSQL 
- SQLAdmin (FastAPI admin for sqlalchemy)
- Docker 
- AS-GI application server (probably Gunicorn)

## Per Requirements
``Docker`` you can take reference from https://docs.docker.com/engine/install/

## Steps to set up

Clone repo on your system using below link

``
git clone git@gitlab.renewbuy.in:gagandeep.singh/boiler-plate.git
``

update postgres credentials accordingly in below-mentioned file

- ./settings.py
- ./migrations/env.py

add ``.env`` file to root directory. take reference from below sample file

### .env
```
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DATABASE=boiler_plate
POSTGRES_USERNAME=renewbuy 
POSTGRES_PASSWORD=Renew2022
```

for testing, you can build docker ``docker-compose build`` and after building docker run the docker using command ``docker-compose up``