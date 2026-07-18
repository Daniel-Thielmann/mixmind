# ADR-003: Pydantic Settings for Application Configuration

## Status

Accepted

## Context

The application requires centralized, validated, and environment-aware configuration. Previously, settings were defined in a `Settings` class using `pydantic.BaseSettings` with minimal validation.

## Decision

Use `pydantic-settings` (v2) with `BaseSettings` as the single source of truth for all configuration. Key design decisions:

- All configuration values come from environment variables (`.env` file)
- Validation with `Field(ge=, le=, pattern=...)` to catch misconfiguration early
- Computed properties (`@property`) for derived paths
- `model_config = SettingsConfigDict(extra="ignore")` to prevent typos from silently passing
- `case_sensitive=True` for consistency

Settings are loaded once at startup via the `lifespan` event and accessed through a module-level `settings` singleton.

## Consequences

- Zero hardcoded secrets — every value is configurable via `.env`
- Type validation at boot prevents runtime configuration errors
- IDE autocompletion for all configuration values
- Environment-specific overrides via `.env.production`, `.env.staging`
