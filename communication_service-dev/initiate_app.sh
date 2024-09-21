#!/bin/bash
set -e

echo "Initiating App. Running migrations"

alembic upgrade head

echo "Migrations applied if any."

uvicorn app.main:app --reload --host 0.0.0.0