#!/bin/sh
set -e

alembic upgrade head

python -u -m app.workers.events_sync_process &
python -u -m app.workers.ticket_outbox_process &
python -u -m app.workers.capashino_outbox_process &

exec "$@"