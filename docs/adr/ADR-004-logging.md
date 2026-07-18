# ADR-004: Structured Logging with JSON-Ready Format

## Status

Accepted

## Context

The application needs a professional logging system that supports structured output, environment-aware verbosity, and future integration with centralized log aggregation (ELK, Grafana Loki, etc.). The initial implementation used `logging.basicConfig` directly in `main.py`.

## Decision

Create a centralized `core/logging.py` module with:

- **`configure_logging()`** — Single function called during application startup
- **Console format** for development: `%(asctime)s | %(levelname)-8s | %(name)s | %(message)s`
- **JSON format** for production: `{"timestamp": "...", "level": "...", "name": "...", "message": "..."}`
- **`LOG_JSON_FORMAT`** setting to toggle between formats via environment variable
- No `print()` statements anywhere in application code
- Library noise suppression: `httpx`, `matplotlib`, `urllib3`, `asyncio` set to WARNING

## Consequences

- Consistent log format across all modules
- Simple transition to JSON logs when integrating with log aggregators
- Environment-aware log levels (DEBUG for development, INFO for production)
- Eliminates scattered `logging.basicConfig()` calls
