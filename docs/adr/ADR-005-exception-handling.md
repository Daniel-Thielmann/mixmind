# ADR-005: Global Exception Handling with Hierarchical Exceptions

## Status

Accepted

## Context

The application needs a consistent, predictable error handling strategy. Unhandled exceptions should return structured error responses without exposing internal details.

## Decision

Implement a hierarchical exception system with global handlers:

- **`AppError`** — Base exception for all application errors
- **`DomainError`** — Domain rule violations (422 Unprocessable Entity)
- **`InfrastructureError`** — External service failures (502 Bad Gateway)
- **`NotFoundError`** — Resource not found (404 Not Found)

Global exception handlers registered in FastAPI:

1. `app_exception_handler` — Catches `AppError` subclasses → JSON response with appropriate status code
2. `global_exception_handler` — Catches unhandled `Exception` → 500 Internal Server Error (no stack trace in response)

All exceptions are logged with request context (path, method) for debugging.

## Consequences

- Consistent error responses across all endpoints
- No sensitive information leaked in error responses
- Easier debugging via structured logging
- Clear separation between expected (AppError) and unexpected (Exception) errors
