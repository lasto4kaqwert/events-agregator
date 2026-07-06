import hashlib
import json
import uuid

from app.schemas.ticket import RegisterTicketSchema


def get_ticket_route_request_hash(
    *,
    event_id: uuid.UUID,
    payload: RegisterTicketSchema,
) -> str:
    data = {
        "event_id": str(event_id),
        "seat": payload.seat.strip(),
        "email": payload.email.strip().lower(),
        "first_name": payload.first_name.strip(),
        "last_name": payload.last_name.strip(),
    }

    raw = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
