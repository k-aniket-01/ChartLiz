#!/bin/bash
# start.sh — dev only

echo "Starting Redis check..."
redis-cli ping || echo "WARNING: Redis not running! Run: redis-server"

echo "Starting Celery Worker..."
celery -A chartliz worker --loglevel=info &

echo "Starting Celery Beat..."
celery -A chartliz beat --loglevel=info &

echo "Starting Django dev server..."
python manage.py runserver