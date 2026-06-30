from enum import Enum


class SyncStatus(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class EventStatus(str, Enum):
    NEW = "new"
    PUBLISHED = "published"
    FINISHED = "finished"
    CLOSED = "registration_closed"


class EventProviderClientType(str, Enum):
    HTTP = "http"
    HTTPS = "https"
