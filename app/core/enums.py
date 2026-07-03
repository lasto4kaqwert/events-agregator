from enum import Enum

######################################################
#   Syncronization
######################################################


class SyncStatus(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

######################################################
#   Events
######################################################


class EventStatus(str, Enum):
    NEW = "new"
    PUBLISHED = "published"
    FINISHED = "finished"
    CLOSED = "registration_closed"

######################################################
#   Tickets
######################################################


class TicketStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"

######################################################
#   Outbox
######################################################


class OutboxStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    FAILED = "failed"


class OutboxEventType(str, Enum):
    TICKET_CREATE_REQUEST = "ticket.create_request"
    TICKET_CANCEL_REQUEST = "ticket.cancel_request"

######################################################
#   Client
######################################################


class EventProviderClientType(str, Enum):
    HTTP = "http"
    HTTPS = "https"
