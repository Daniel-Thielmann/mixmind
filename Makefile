.PHONY: run test lint format typecheck coverage docker-up docker-down clean

# ---- Development ----

run:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	cd backend && python -m pytest -x -q

coverage:
	cd backend && python -m pytest --cov --cov-report=term-missing

# ---- Code Quality ----

lint:
	ruff check backend/

format:
	ruff format backend/

typecheck:
	mypy backend/app/

check: lint format typecheck test

# ---- Docker ----

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

# ---- Cleanup ----

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
