.PHONY: help dev down test lint build check prod-config

help: ## Show available project commands.
	@awk 'BEGIN {FS = ":.*## "; print "Chess Coach commands:"} /^[a-zA-Z_-]+:.*## / {printf "  %-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## Start the complete development stack.
	docker compose -f docker-compose.dev.yml up --build

down: ## Stop the development stack.
	docker compose -f docker-compose.dev.yml down

test: ## Run frontend and Python service tests.
	cd chess-ui && npm run test
	cd game-scraper && python -m pytest -q
	cd coach-ai && python -m pytest -q

lint: ## Run frontend lint checks.
	cd chess-ui && npm run lint

build: ## Build the production frontend.
	cd chess-ui && VITE_APP_MODE=production npm run build

prod-config: ## Validate the production Docker Compose configuration.
	docker compose config --quiet

check: test lint build prod-config ## Run the same core checks used by CI.
