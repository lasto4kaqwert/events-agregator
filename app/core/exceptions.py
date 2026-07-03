class EventNotFoundError(Exception):
    pass


class SeatIsNotAvaiableError(Exception):
    pass


class SynchronizationNotFoundError(Exception):
    pass


class ExternalAPIError(Exception):
    pass

######################################################
#   Ticket Exceptions
######################################################


class TicketNotFoundError(Exception):
    pass


class TicketConflictError(Exception):
    pass

######################################################
#   Outbox Exceptions
######################################################


class OutboxNotFoundError(Exception):
    pass


class OutboxConflictError(Exception):
    pass
