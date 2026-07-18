# Coding Standards

Always follow SOLID.

Prefer composition over inheritance.

Never duplicate code.

Always use type hints.

Always write docstrings.

Use pathlib instead of os whenever possible.

Prefer Pydantic models over raw dictionaries.

---

# API Rules

Endpoints must:

- Validate
- Call services
- Return schemas

Nothing else.

---

# Services

Services receive domain objects.

Services return domain objects.

Never return raw JSON.

Never know FastAPI.

---

# Schemas

Schemas represent data only.

No business logic.

---

# Utilities

Utility functions must be pure.

No side effects.

---

# Testing

Every feature must include tests.

Coverage must never decrease.

Existing tests must continue passing.

---

# Formatting

Always pass:

ruff

black

isort

pytest

before commit.

---

# Git

Never commit directly to main.

Use feature branches.

Merge only after all checks pass.

---

# Response Pattern

Whenever implementing a feature:

Explain:

- What changed
- Files created
- Files modified
- Architectural decisions
- Manual testing
- Next recommended feature

==========================================================
ENTREGA OBRIGATÓRIA
==========================================================

Ao finalizar TODAS as alterações, NÃO responda apenas dizendo que concluiu.

Sua resposta DEVE conter obrigatoriamente:

# 1. Resumo Executivo

Explique em poucas linhas o que foi implementado.

---

# 2. Diff dos Arquivos

Liste TODOS os arquivos criados, modificados, renomeados e removidos.

Utilize exatamente o formato abaixo:

## Arquivos Criados

- backend/app/core/config.py
- backend/app/core/logging.py
- backend/app/core/security.py
- backend/app/core/exceptions.py
- backend/app/core/constants.py
  ...

## Arquivos Modificados

M backend/pyproject.toml

M backend/Dockerfile

M docker-compose.yml

...

## Arquivos Removidos

- backend/requirements.txt

...

---

# 3. Estrutura Final

Mostre a árvore completa do backend após todas as alterações.

Utilize o comando tree como referência.

---

# 4. Justificativa Técnica

Explique o motivo técnico de CADA alteração importante.

Por exemplo:

- por que requirements.txt foi removido
- por que uv foi escolhido
- por que Ruff substitui Black + Flake8
- por que MyPy foi configurado
- por que Settings utiliza Pydantic
- por que Logging foi centralizado
- por que Exceptions são globais

Não apenas diga "foi alterado".

Explique a decisão de engenharia.

---

# 5. Comandos Novos

Liste todos os comandos disponíveis após a Sprint.

Exemplo:

uv sync

uv run uvicorn ...

uv run pytest

uv run ruff check

uv run ruff format

uv run mypy

etc.

---

# 6. Checklist da Sprint

Mostre exatamente este checklist.

[✓] Migração para uv

[✓] pyproject.toml

[✓] Ruff

[✓] MyPy

[✓] Pytest

[✓] Logging

[✓] Settings

[✓] Health Endpoint

...

---

# 7. Próximas Pendências

Liste apenas o que NÃO foi implementado porque pertence à Sprint 3.

---

# 8. IMPORTANTE

Não cole arquivos inteiros na resposta.

Não explique código linha por linha.

Forneça apenas o relatório técnico e o diff dos arquivos.

==========================================================

IMPORTANTE

Se alguma decisão arquitetural parecer ambígua, NÃO invente uma solução.

Escolha a alternativa mais utilizada na indústria e documente a decisão no relatório final.
