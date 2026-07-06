#!/usr/bin/env bash
# Build script for Render (Build Command: ./build.sh).
# Installs dependencies, collects static files, migrates, seeds demo data,
# and ensures an admin user exists.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Seed demo categories/dishes (idempotent) and regenerate their images.
python manage.py seed_menu

# Create the admin user from DJANGO_SUPERUSER_* env vars if it doesn't exist.
# The "|| true" keeps redeploys from failing once the user already exists.
python manage.py createsuperuser --no-input || true
