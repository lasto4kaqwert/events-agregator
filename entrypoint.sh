#!/bin/sh
set -e

alembic upgrade head

python -u -m app.workers.events_sync_process &

uvicorn app.main:app --host 0.0.0.0 --port 8000 &

wait