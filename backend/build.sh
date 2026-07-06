#!/usr/bin/env bash
# Build script for Render (Build Command: ./build.sh).
# Installs dependencies, collects static files and applies migrations.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
