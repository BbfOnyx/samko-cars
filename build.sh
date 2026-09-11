#!/usr/bin/env bash
# Render Build Script for Samko Cars
set -o errexit

echo "==> Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running database migrations..."
python manage.py migrate --no-input

echo "==> Seeding initial configuration & demo inventory if database is empty..."
python manage.py seed_cars --quiet

echo "==> Build complete successfully!"
