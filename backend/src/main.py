"""
Prompt-Boost v2.0 Backend - Main Application
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.config import settings
from src.utils.logger import setup_logging
from src.api import recursion_router, websocket_router
from src.api.compatibility import router as compatibility_router


# Prometheus metrics - HTTP
REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# Prometheus metrics - Users and Sessions
ACTIVE_USERS = Gauge(
    "active_users_gauge",
    "Number of active users",
)
SESSIONS_RUNNING = Gauge(
    "recursion_sessions_running_gauge",
    "Number of recursion sessions currently running",
)
SESSIONS_TOTAL = Counter(
    "recursion_sessions_total",
    "Total recursion sessions",
    ["technique", "status"],
)
SESSION_DURATION_SECONDS = Histogram(
    "recursion_session_duration_seconds",
    "Recursion session duration in seconds",
    ["technique", "status"],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0),
)

# Prometheus metrics - LLM Usage
TOKENS_USED = Counter(
    "tokens_used_total",
    "Total tokens used",
    ["provider", "model"],
)
LLM_API_CALLS = Counter(
    "llm_api_calls_total",
    "Total LLM API calls",
    ["provider", "model", "status"],
)
LLM_API_ERRORS = Counter(
    "llm_api_errors_total",
    "Total LLM API errors",
    ["provider", "error_type"],
)
LLM_API_DURATION_SECONDS = Histogram(
    "llm_api_duration_seconds",
    "LLM API call duration in seconds",
    ["provider", "model"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
)

# Prometheus metrics - Database
DB_QUERY_DURATION_SECONDS = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
    buckets=(0.001, 0.01, 0.05, 0.1, 0.5, 1.0),
)
DB_CONNECTIONS = Gauge(
    "db_connections_gauge",
    "Current database connections",
)

# Prometheus metrics - Cache
CACHE_HITS = Counter(
    "cache_hits_total",
    "Total cache hits",
    ["cache_name"],
)
CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total cache misses",
    ["cache_name"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP metrics."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        start_time = time.time()
        endpoint = request.url.path

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            
            # Record metrics
            REQUESTS_TOTAL.labels(
                method=request.method,
                endpoint=endpoint,
                status=status_code,
            ).inc()
            REQUEST_DURATION_SECONDS.labels(
                method=request.method,
                endpoint=endpoint,
            ).observe(duration)

        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan - startup and shutdown events."""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("🚀 Prompt-Boost Backend v2.0.0 starting...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Initialize database on startup
    try:
        from src.models import init_db
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️  Database not available: {e}")

    yield

    logger.info("🛑 Prompt-Boost Backend shutting down...")


app = FastAPI(
    title="Prompt-Boost v2.0.0 API",
    description="Recursive Reasoning Platform with 7 LLM Techniques",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(compatibility_router)
app.include_router(recursion_router)
app.include_router(websocket_router)


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": "Prompt-Boost v2.0.0",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
    }


@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )