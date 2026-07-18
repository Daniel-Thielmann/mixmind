# ADR-002: Clean Architecture with Domain-Driven Design

## Status

Accepted

## Context

The backend needs a sustainable architecture that separates concerns, allows independent evolution of layers, and follows industry best practices. The initial implementation placed all modules under a flat `app/` package.

## Decision

Adopt Clean Architecture with DDD-inspired layering:

- **`domain/`** — Enterprise business rules: entities, value objects, repository interfaces. Framework-agnostic.
- **`application/`** — Application business rules: use cases, DTOs, port interfaces. Orchestrates domain logic.
- **`infrastructure/`** — External concerns: LLM clients, audio processing, storage, database. Implements ports.
- **`api/`** — Interface adapters: FastAPI routers, endpoints, request/response handling.
- **`core/`** — Cross-cutting: configuration, logging, exceptions, security, constants.
- **`shared/`** — Utilities justified to not belong in any other layer.

Each layer depends only on layers below it (domain ← application ← infrastructure ← api).

## Consequences

- Business logic is isolated from frameworks and external services
- Ports (interfaces) in domain/application allow swapping infrastructure implementations
- New features follow a consistent, predictable pattern
- Increased initial structure, but reduced technical debt over time
