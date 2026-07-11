"""
ATLAS Platform - Main FastAPI Application

This is the main entry point for the ATLAS Platform API.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.v1.router import api_router
from backend.core.config import get_settings
from backend.core.logging import get_logger, setup_logging
from backend.db import close_db, init_db

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "Starting ATLAS Platform",
        version=get_settings().app.version,
        environment=get_settings().app.environment,
    )

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("Shutting down ATLAS Platform")
    await close_db()
    logger.info("Shutdown complete")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app.name,
        description=settings.app.description,
        version=settings.app.version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router, prefix=settings.app.api_v1_prefix)

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle uncaught exceptions."""
        logger.error(
            "Unhandled exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            exc_info=True,
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(exc) if settings.app.debug else None,
            },
        )

    # Root endpoint
    @app.get("/")
    async def root() -> dict:
        """Root endpoint returning API information."""
        return {
            "name": settings.app.name,
            "version": settings.app.version,
            "description": settings.app.description,
            "docs": "/docs",
            "health": "/health",
        }

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy",
            "version": settings.app.version,
            "environment": settings.app.environment,
        }

    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "backend.api.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug,
        workers=1 if settings.app.debug else settings.app.workers,
    )
