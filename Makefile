# Plateful AI Makefile
.DEFAULT_GOAL := precommit

.PHONY: help dev fix lint-verify test test-coverage precommit clean

# API defaults
API_HOST ?= localhost
API_PORT ?= 8081

help:
	@echo "Plateful AI - Available Commands:"
	@echo ""
	@echo "  Application:"
	@echo "  make dev             - Start API server with hot-reload"
	@echo ""
	@echo "  Code Quality:"
	@echo "  make fix             - Auto-format code (ruff format + ruff check --fix)"
	@echo "  make lint-verify     - Verify formatting and lint (no writes)"
	@echo "  make precommit       - Full pipeline: fix → lint → test"
	@echo ""
	@echo "  Testing:"
	@echo "  make test            - Run all tests"
	@echo "  make test-coverage   - Run tests with coverage report"
	@echo ""
	@echo "  Utilities:"
	@echo "  make clean           - Remove caches and temp files"

# ================================================================================
# Application Commands
# ================================================================================
dev:
	@uv run uvicorn recipe_app.main:app --reload --host 0.0.0.0 --port $(API_PORT)

# ================================================================================
# Code Quality
# ================================================================================
fix:
	@uv run ruff format recipe_app/ tests/
	@uv run ruff check --fix recipe_app/ tests/

lint-verify:
	@uv run ruff format --check recipe_app/ tests/
	@uv run ruff check recipe_app/ tests/

# ================================================================================
# Testing
# ================================================================================
test:
	@uv run pytest tests/ -x -q --tb=short

test-coverage:
	@uv run pytest tests/ -v --cov=recipe_app --cov-report=html --cov-report=term-missing --cov-branch

# ================================================================================
# Utilities
# ================================================================================
clean:
	@find . -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
	@rm -f .coverage
	@rm -rf htmlcov/
	@echo "Cleaned."

# ================================================================================
# Precommit Pipeline
# ================================================================================
precommit:
	@start=$$(date +%s); \
	failed=""; \
	echo ""; \
	echo "========================================================================"; \
	echo "                   PLATEFUL AI — PRECOMMIT CHECKS                      "; \
	echo "========================================================================"; \
	echo ""; \
	echo "[1/3] Auto-fix (ruff format + check --fix)..."; \
	if $(MAKE) -s fix; then \
		echo "      ✓ Code formatted"; \
	else \
		echo "      ✗ Auto-fix failed"; \
		failed="$$failed fix"; \
	fi; \
	echo ""; \
	echo "[2/3] Lint verify (ruff format --check + check)..."; \
	if $(MAKE) -s lint-verify; then \
		echo "      ✓ Lint passed"; \
	else \
		echo "      ✗ Lint failed"; \
		failed="$$failed lint"; \
	fi; \
	echo ""; \
	echo "[3/3] Tests (pytest)..."; \
	if $(MAKE) -s test; then \
		echo "      ✓ All tests passed"; \
	else \
		echo "      ✗ Tests failed"; \
		failed="$$failed tests"; \
	fi; \
	echo ""; \
	echo "========================================================================"; \
	end=$$(date +%s); \
	dur=$$((end-start)); \
	if [ -z "$$failed" ]; then \
		echo "  ALL CHECKS PASSED ($$dur seconds)"; \
	else \
		echo "  CHECKS FAILED ($$dur seconds):$$failed"; \
		echo "========================================================================"; \
		echo ""; \
		exit 1; \
	fi; \
	echo "========================================================================"; \
	echo ""
