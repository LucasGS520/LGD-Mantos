"""Middleware ASGI: correlaciona erros e tempos sem ler corpo, token ou query."""

import time
from uuid import uuid4

from app.shared.application.telemetry import emit, request_id


class RequestTelemetry:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        correlation = uuid4().hex
        context = request_id.set(correlation)
        started, status = time.perf_counter(), 500

        async def observed(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                message["headers"] = [
                    *message.get("headers", []),
                    (b"x-request-id", correlation.encode()),
                ]
            await send(message)

        try:
            await self.app(scope, receive, observed)
        finally:
            route = scope.get("route")
            emit(
                "request",
                method=scope["method"],
                route=getattr(route, "path", "unmatched"),
                status=status,
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
            )
            request_id.reset(context)
