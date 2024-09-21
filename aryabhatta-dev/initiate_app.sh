#!/bin/bash
set -e

echo "-----Starting Pricing Service-----"
# uncomment to create migrations (required for local development)
# alembic revision --autogenerate -m "new_models"
echo "Running migrations"
alembic upgrade head
echo "Migrations done..."

echo "Running application"
uvicorn app.main:app --host 0.0.0.0
