"""
Prompt-Boost v2.0 Backend - Main Application
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

from src.config import settings
from src.utils.logger import setup_logging


# Prometheus metrics
REQUESTS_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
ACTIVE_USERS = Gauge(
    "active_users",
    "Number of active users",
)
SESSIONS_RUNNING = Gauge(
    "recursion_sessions_running",
    "Number of recursion sessions currently running",
)
SESSIONS_TOTAL = Counter(
    "recursion_sessions_total",
    "Total recursion sessions",
    ["technique", "status"],
)
TOKENS_USED = Counter(
    "tokens_used_total",
    "Total tokens used",
    ["provider", "model"],
)


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
async def metrics() -> tuple[bytes, dict]:
    """Prometheus metrics endpoint."""
    return (
        generate_latest(),
        {"Content-Type": CONTENT_TYPE_LATEST},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )