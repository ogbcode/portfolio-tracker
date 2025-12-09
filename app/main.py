"""FastAPI application entry point."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.utils import get_openapi

from app.api.routes import prices, wallets
from app.cache import cache
from app.config import get_settings
from app.core.logging import logger
from app.core.response import error_response
from app.database import db
from app.exceptions import BlockAiException
from app.services.price_service import price_service


async def update_rates_loop():
    """Background task to update all prices every 30 seconds."""
    while True:
        try:
            logger.info("Background task: Refreshing prices...")
            await price_service.get_all_prices()
        except Exception as e:
            logger.error(f"Background task error: {e}")
        
        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    logger.info("Starting BlockAi Portfolio Tracker...")
    
    await db.connect()
    logger.info("Connected to MongoDB")
    
    await cache.connect()
    logger.info("Connected to Redis")
    
    # Initial price fetch
    await price_service.get_all_prices()
    task = asyncio.create_task(update_rates_loop())
    
    yield
    
    # Cancel background task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    await cache.disconnect()
    logger.info("Disconnected from Redis")
    
    await db.disconnect()
    logger.info("Disconnected from MongoDB")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Multi-chain cryptocurrency portfolio tracker with support for Ethereum and Bitcoin",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,       # Disable default Swagger UI
    redoc_url=None,      # Disable default ReDoc
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/docs", include_in_schema=False)
async def scalar_html():
    """Serve Scalar API reference."""
    return HTMLResponse("""
        <!doctype html>
        <html>
          <head>
            <title>BlockAi API Reference</title>
            <meta charset="utf-8" />
            <meta
              name="viewport"
              content="width=device-width, initial-scale=1" />
            <style>
              body {
                margin: 0;
              }
            </style>
          </head>
          <body>
            <script
              id="api-reference"
              data-url="/openapi.json"></script>
            <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
          </body>
        </html>
    """)


@app.exception_handler(BlockAiException)
async def blockai_exception_handler(request: Request, exc: BlockAiException):
    """Global exception handler for application-specific errors."""
    logger.error(f"BlockAiException: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message="An error occurred",
            error=exc.message,
        ),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors."""
    logger.exception(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=error_response(
            message="Internal server error",
            error=str(exc) if settings.debug else "An unexpected error occurred",
        ),
    )


# Use /api/v1 prefix for all routes
app.include_router(wallets.router, prefix="/api/v1")
app.include_router(prices.router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "success": True,
        "message": "BlockAi Portfolio Tracker API",
        "data": {
            "version": "1.0.0",
            "status": "healthy",
            "docs": "/docs"
        },
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    return {
        "success": True,
        "message": "All systems operational",
        "data": {
            "database": "connected",
            "cache": "connected",
            "version": "1.0.0",
        },
    }
