# GitHub Copilot Instructions

Always preserve the existing architecture.

Before implementing any feature:

- Analyze the current project structure.
- Reuse existing services whenever possible.
- Do not duplicate code.
- Respect SOLID principles.
- Keep business logic inside services.
- Keep endpoints thin.
- Prefer composition over inheritance.
- Always use full type hints.
- Always create or update automated tests.
- Do not introduce breaking changes.
- Keep responses strongly typed using Pydantic models.

Every implementation must be production-ready.

The project prioritizes maintainability, scalability and readability over speed.

When a feature is completed, always provide:

- Summary
- Files created
- Files modified
- Architectural decisions
- Manual testing instructions
- Suggested next feature
