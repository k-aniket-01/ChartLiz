#!/bin/bash

echo "Starting Celery Worker..."
celery -A chartliz worker --loglevel=info --pool=solo --concurrency=1 &

echo "Starting Celery Beat..."
celery -A chartliz beat --loglevel=info &

echo "Starting Django..."
gunicorn chartliz.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --workers 1 \
  --bind 0.0.0.0:$PORT