#!/bin/bash
set -e

#echo "Creating migrations"
#alembic revision --autogenerate -m "Added tables for RBAC"
#echo "done"

echo "Initiating App. Running migrations"

alembic upgrade head

echo "Migrations applied if any."

uvicorn main:app --host 0.0.0.0