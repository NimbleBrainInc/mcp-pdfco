# MCPB bundle configuration
BUNDLE_NAME = mcp-pdfco
VERSION ?= 0.1.2

.PHONY: help install dev-install format format-check lint lint-fix typecheck test test-cov test-e2e clean run check all bundle bundle-run bundle-clean

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

format-check: ## Check code formatting with ruff
	uv run ruff format --check src/ tests/

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

test-e2e: ## Run end-to-end API tests (requires PDFCO_API_KEY)
	uv run pytest e2e/ -v -s

clean: ## Clean up artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf bundle/ dist/ *.mcpb

run: ## Run the MCP server (stdio mode)
	uv run python -m mcp_pdfco.server

check: format-check lint typecheck test ## Run all checks

all: clean dev-install format lint typecheck test ## Full workflow

# MCPB bundle commands
bundle: ## Build MCPB bundle to dist/
	@echo "Building MCPB bundle..."
	@rm -rf bundle/ dist/
	@mkdir -p bundle dist
	@# Copy source files (module at bundle root for python -m imports)
	@cp -r src/mcp_pdfco bundle/
	@cp manifest.json bundle/
	@cp pyproject.toml bundle/
	@cp README.md bundle/ 2>/dev/null || true
	@# Install dependencies into bundle
	@uv pip compile pyproject.toml --quiet > /tmp/requirements.txt
	@cd bundle && uv pip install --target deps/ -r /tmp/requirements.txt
	@rm /tmp/requirements.txt
	@# Pack the bundle
	mcpb pack bundle/ dist/$(BUNDLE_NAME)-v$(VERSION).mcpb
	@rm -rf bundle/
	@echo "Bundle created: dist/$(BUNDLE_NAME)-v$(VERSION).mcpb"

bundle-run: bundle ## Build and run bundle interactively
	mpak run --local dist/$(BUNDLE_NAME)-v$(VERSION).mcpb

bundle-clean: ## Clean bundle artifacts
	rm -rf bundle/ dist/

# Aliases
fmt: format
t: test
l: lint
