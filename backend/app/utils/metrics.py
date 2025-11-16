"""Prometheus metrics for monitoring."""
from prometheus_client import Counter, Histogram, Gauge, REGISTRY
import time

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Business metrics
analyses_created_total = Counter(
    'analyses_created_total',
    'Total number of analyses created',
    ['mood_id']
)

analyses_failed_total = Counter(
    'analyses_failed_total',
    'Total number of failed analyses',
    ['error_type']
)

datasets_generated_total = Counter(
    'datasets_generated_total',
    'Total number of datasets generated'
)

models_trained_total = Counter(
    'models_trained_total',
    'Total number of models trained'
)

users_registered_total = Counter(
    'users_registered_total',
    'Total number of users registered'
)

# Quota metrics
quota_exceeded_total = Counter(
    'quota_exceeded_total',
    'Total number of quota exceeded events',
    ['resource']
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total number of cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total number of cache misses',
    ['cache_type']
)

# Database metrics
db_queries_total = Counter(
    'db_queries_total',
    'Total number of database queries',
    ['table']
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['table']
)

# Current state gauges
active_users_gauge = Gauge(
    'active_users',
    'Number of currently active users'
)

pending_tasks_gauge = Gauge(
    'pending_tasks',
    'Number of pending background tasks'
)


# Middleware for tracking HTTP metrics
class PrometheusMiddleware:
    """FastAPI middleware to track HTTP metrics."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]

        # Skip metrics endpoint itself
        if path == "/metrics":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        status_code = 500  # Default to error

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Record metrics
            duration = time.time() - start_time
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status=status_code
            ).inc()
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)
