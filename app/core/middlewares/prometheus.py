import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import HTTP_DURATION, HTTP_REQUESTS


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        started_at = time.monotonic()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            HTTP_REQUESTS.labels(
                method=request.method,
                endpoint=request.url.path,
                status=str(status_code),
            ).inc()

            HTTP_DURATION.labels(
                method=request.method,
                endpoint=request.url.path,
            ).observe(time.monotonic() - started_at)
