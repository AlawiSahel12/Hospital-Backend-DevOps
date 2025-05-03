#!/bin/sh
set -e

echo "Waiting for the database to be ready..."
python manage.py wait_for_db

echo "Applying migrations..."
python manage.py migrate

echo "Running isort for Django imports..."
isort .

echo "Starting the server..."
exec python manage.py runserver 0.0.0.0:8000