#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies from root requirements.txt
pip install -r requirements.txt

# Enter the django project folder to run management commands
cd backend

# Collect static files for WhiteNoise
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate