IMAGE_NAME = nimbletools/mcp-pdfco
VERSION ?= 2.0.0

.PHONY: help install dev-install format lint test clean run check all docker-build release docker-run test-e2e

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	uv pip install -e .

dev-install: ## Install with dev dependencies
	uv pip install -e ".[dev]"

format: ## Format code with ruff
	uv run ruff format src/ tests/

lint: ## Lint code with ruff
	uv run ruff check src/ tests/

lint-fix: ## Lint and fix code with ruff
	uv run ruff check --fix src/ tests/

typecheck: ## Type check with mypy
	uv run mypy src/

test: ## Run tests with pytest
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage
	uv run pytest tests/ -v --cov=src/mcp_pdfco --cov-report=term-missing

test-e2e: ## Run end-to-end Docker tests
	uv run pytest e2e/ -v -s

clean: ## Clean up artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

run: ## Run the MCP server (stdio mode)
	uv run python -m mcp_pdfco.server

run-http: ## Run HTTP server with uvicorn
	uv run uvicorn mcp_pdfco.server:app --host 0.0.0.0 --port 8100

check: lint typecheck test ## Run all checks

all: clean install format lint typecheck test ## Full workflow

# Docker commands
docker-build: ## Build Docker image locally
	docker build -t $(IMAGE_NAME):$(VERSION) -t $(IMAGE_NAME):latest .

docker-run: ## Run Docker container
	docker run -e ABSTRACT_API_KEY=$(ABSTRACT_API_KEY) -p 8000:8000 $(IMAGE_NAME):$(VERSION)

release: ## Build and push multi-platform Docker image
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t $(IMAGE_NAME):$(VERSION) \
		-t $(IMAGE_NAME):latest \
		--push .

# Aliases
fmt: format
t: test
l: lint
