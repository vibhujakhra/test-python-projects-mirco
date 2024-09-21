#!/bin/bash
set -e

echo "Initiating App. Running migrations"

alembic upgrade head

echo "Migrations applied if any."

uvicorn app.main:app --host 0.0.0.0