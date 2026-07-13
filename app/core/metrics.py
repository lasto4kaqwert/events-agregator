from prometheus_client import Counter, Gauge, Histogram

BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "HTTP Total Requests",
    ("method", "endpoint", "status"),
)
HTTP_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP latency",
    ("method", "endpoint"),
    buckets=BUCKETS,
)

PROVIDER_REQUESTS = Counter(
    "events_provider_requests_total",
    "Provider Total Requests",
    ("endpoint", "status"),
)
PROVIDER_DURATION = Histogram(
    "events_provider_request_duration_seconds",
    "Provider latency",
    ("endpoint",),
    buckets=BUCKETS,
)

TICKETS_CREATED = Gauge(
    "tickets_created_total",
    "Created tickets in DB",
)
TICKETS_CANCELLED = Gauge(
    "tickets_cancelled_total",
    "Cancelled tickets in DB",
)
EVENTS_TOTAL = Gauge(
    "events_total",
    "Total events in DB",
)

CACHE_HITS = Counter(
    "cache_hits_total",
    "Cache hits (seats)",
)
CACHE_MISSES = Counter(
    "cache_misses_total",
    "Cache misses (seats)",
)
