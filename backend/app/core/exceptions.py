from __future__ import annotations

import logging
import traceback

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "An unexpected error occurred"

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class DomainError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class InfrastructureError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND


class AudioAnalysisException(HTTPException):
    def __init__(self, filename: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to analyze audio file: {filename}",
        )


class InvalidAudioFileException(HTTPException):
    def __init__(self, filename: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format: {filename}",
        )


class InvalidMediaFileException(HTTPException):
    def __init__(self, filename: str, reason: str = "Invalid media file") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{reason}: {filename}",
        )


class FileTooLargeException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded file exceeds maximum allowed size.",
        )


class SpotifyAuthenticationError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Spotify authentication failed. Please reconnect your Spotify account."


class SpotifyTrackNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Spotify track not found."


class SpotifyMetadataError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "Failed to retrieve track metadata from Spotify."


class SpotifyApiError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY

    def __init__(self, detail: str = "Spotify API request failed.") -> None:
        super().__init__(detail=detail)


class AudioProviderUnavailableError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "The external audio provider is temporarily unavailable."


class AudioDownloadNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Audio download not found for the requested track."


class AudioDownloadTimeoutError(AppError):
    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    detail = "Audio download timed out."


class AudioDownloadTooLargeError(AppError):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    detail = "Downloaded audio exceeds maximum allowed size."


class InvalidDownloadedAudioError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    detail = "Downloaded audio file is invalid or corrupted."


class AudioDurationMismatchError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    detail = "Downloaded audio duration does not match Spotify track metadata."


class ExternalProviderRateLimitError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Rate limit exceeded for the external audio provider."


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception | path=%s | method=%s | error=%s",
        request.url.path,
        request.method,
        str(exc),
    )
    logger.debug(
        "Traceback:\n%s",
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred"},
    )


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning(
        "Application exception | path=%s | method=%s | status=%d | detail=%s",
        request.url.path,
        request.method,
        exc.status_code,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
