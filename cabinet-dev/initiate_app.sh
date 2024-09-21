#!/bin/bash
set -e

echo "Migrations applied if any."

uvicorn main:app --host 0.0.0.0