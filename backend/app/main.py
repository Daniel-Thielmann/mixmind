from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.api.router import api_router
from app.core.config import settings
from app.core.constants import APP_NAME, APP_VERSION
from app.core.exceptions import (
    AppError,
    app_exception_handler,
    global_exception_handler,
)
from app.core.logging import configure_logging, get_logger
from app.core.security import build_cors_origins
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging(
        log_level=settings.LOG_LEVEL,
        json_format=settings.LOG_JSON_FORMAT,
        app_name=settings.APP_NAME,
    )
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Environment: %s", settings.ENVIRONMENT)

    settings.upload_path.mkdir(parents=True, exist_ok=True)
    settings.processed_path.mkdir(parents=True, exist_ok=True)
    settings.temp_path.mkdir(parents=True, exist_ok=True)

    yield

    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
)


cors_origins = (
    settings.CORS_ORIGINS
    if settings.CORS_ORIGINS
    else build_cors_origins(environment=settings.ENVIRONMENT)
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.mount(
    "/processed",
    StaticFiles(directory=settings.processed_path),
    name="processed",
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

app.add_exception_handler(AppError, app_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, global_exception_handler)


@app.get("/", tags=["Health"])
async def root_health() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "project": APP_NAME,
            "version": APP_VERSION,
            "status": "running",
            "environment": settings.ENVIRONMENT,
        },
    )
