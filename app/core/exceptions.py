class EventNotFoundError(Exception):
    pass


class SeatIsNotAvaiableError(Exception):
    pass


class SynchronizationNotFoundError(Exception):
    pass

######################################################
#   Ticket Exceptions
######################################################


class ExternalAPIError(Exception):
    pass


class ExternalAPIUnauthorizedError(ExternalAPIError):
    pass

######################################################
#   Ticket Exceptions
######################################################


class TicketNotFoundError(Exception):
    pass


class TicketConflictError(Exception):
    pass


class TicketOccupiedError(Exception):
    pass


class TicketIdempotencyConflictError(Exception):
    pass

######################################################
#   Outbox Exceptions
######################################################


class OutboxNotFoundError(Exception):
    pass


class OutboxConflictError(Exception):
    pass

######################################################
#   Outbox Exceptions
######################################################


class CapashinoError(Exception):
    pass


class CapashinoInvalidBodyError(CapashinoError):
    pass


class CapashinoInvalidApiKeyError(CapashinoError):
    pass


class CapashinoIdempotencyParsedError(CapashinoError):
    pass


class CapashinoEmptyMessageError(CapashinoError):
    pass


class CapashinoRepeatEncounterError(CapashinoError):
    pass
