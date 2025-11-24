.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser test lint format clean

# Variables
DOCKER_COMPOSE = docker-compose
DOCKER_EXEC = docker-compose exec web
PYTHON = python
MANAGE = $(PYTHON) manage.py

# Colors for terminal output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)Content Hub API - Available Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Docker Commands
build: ## Build Docker containers
	@echo "$(GREEN)Building Docker containers...$(NC)"
	$(DOCKER_COMPOSE) build

up: ## Start all services in detached mode
	@echo "$(GREEN)Starting all services...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Services started! Access the app at http://localhost$(NC)"
	@echo "$(YELLOW)API Documentation: http://localhost/api/docs/$(NC)"
	@echo "$(YELLOW)Admin Panel: http://localhost/admin/$(NC)"

down: ## Stop all services
	@echo "$(RED)Stopping all services...$(NC)"
	$(DOCKER_COMPOSE) down

restart: down up ## Restart all services

logs: ## View logs from all services
	$(DOCKER_COMPOSE) logs -f

logs-web: ## View logs from web service only
	$(DOCKER_COMPOSE) logs -f web

logs-db: ## View logs from database service only
	$(DOCKER_COMPOSE) logs -f db

ps: ## List running containers
	$(DOCKER_COMPOSE) ps

# Development Commands
shell: ## Open Django shell
	$(DOCKER_EXEC) $(MANAGE) shell

bash: ## Open bash shell in web container
	$(DOCKER_EXEC) bash

dbshell: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) exec db psql -U postgres -d content_hub_db

# Database Commands
migrate: ## Run database migrations
	@echo "$(GREEN)Running migrations...$(NC)"
	$(DOCKER_EXEC) $(MANAGE) migrate

makemigrations: ## Create new migrations
	@echo "$(GREEN)Creating migrations...$(NC)"
	$(DOCKER_EXEC) $(MANAGE) makemigrations

showmigrations: ## Show migration status
	$(DOCKER_EXEC) $(MANAGE) showmigrations

createsuperuser: ## Create Django superuser
	$(DOCKER_EXEC) $(MANAGE) createsuperuser

# Data Management
loaddata: ## Load fixture data
	$(DOCKER_EXEC) $(MANAGE) loaddata fixtures/*.json

dumpdata: ## Dump data to fixtures
	$(DOCKER_EXEC) $(MANAGE) dumpdata --indent=2 -o fixtures/data.json

flush: ## Flush database (WARNING: deletes all data)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_EXEC) $(MANAGE) flush --noinput; \
	fi

# Static Files
collectstatic: ## Collect static files
	@echo "$(GREEN)Collecting static files...$(NC)"
	$(DOCKER_EXEC) $(MANAGE) collectstatic --noinput

# Code Quality
lint: ## Run linters
	@echo "$(GREEN)Running linters...$(NC)"
	$(DOCKER_EXEC) flake8 apps config core
	$(DOCKER_EXEC) pylint apps config core

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	$(DOCKER_EXEC) black apps config core
	$(DOCKER_EXEC) isort apps config core

format-check: ## Check code formatting without making changes
	$(DOCKER_EXEC) black --check apps config core
	$(DOCKER_EXEC) isort --check-only apps config core

type-check: ## Run type checking with mypy
	$(DOCKER_EXEC) mypy apps config core

# Cleanup
clean: ## Remove Python cache files
	@echo "$(GREEN)Cleaning Python cache files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.py~" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

clean-docker: ## Remove all Docker containers, volumes, and images
	@echo "$(RED)Removing all Docker resources...$(NC)"
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -af

# Environment Setup
env: ## Create .env file from .env.example
	@if [ ! -f .env ]; then \
		echo "$(GREEN)Creating .env file from .env.example...$(NC)"; \
		cp .env.example .env; \
		echo "$(YELLOW)⚠️  Please review and update .env file with your settings$(NC)"; \
	else \
		echo "$(YELLOW).env file already exists$(NC)"; \
	fi

# Initial Setup
setup: env build up migrate createsuperuser collectstatic ## Complete initial setup (one command to rule them all!)
	@echo "$(GREEN)✓ Setup complete! Your app is ready.$(NC)"
	@echo ""
	@echo "$(GREEN)Access your API:$(NC)"
	@echo "  • API: http://localhost/api/v1/"
	@echo "  • Swagger Docs: http://localhost/api/docs/"
	@echo "  • Admin Panel: http://localhost/admin/"

quick-start: build up ## Quick start without migrations
	@echo "$(GREEN)Quick start complete!$(NC)"
	@echo "$(YELLOW)Don't forget to run 'make migrate' if needed$(NC)"

# Cache Management
clear-cache: ## Clear Redis cache
	$(DOCKER_COMPOSE) exec redis redis-cli FLUSHALL

# Backup & Restore
backup-db: ## Backup database to file
	@echo "$(GREEN)Backing up database...$(NC)"
	$(DOCKER_COMPOSE) exec -T db pg_dump -U postgres content_hub_db > backup_$$(date +%Y%m%d_%H%M%S).sql

restore-db: ## Restore database from file (usage: make restore-db FILE=backup.sql)
	@echo "$(YELLOW)Restoring database from $(FILE)...$(NC)"
	$(DOCKER_COMPOSE) exec -T db psql -U postgres content_hub_db < $(FILE)

# Production Commands
prod-up: ## Start services in production mode
	@echo "$(GREEN)Starting production services...$(NC)"
	DJANGO_SETTINGS_MODULE=config.settings.production $(DOCKER_COMPOSE) up -d

prod-build: ## Build for production
	DJANGO_SETTINGS_MODULE=config.settings.production $(DOCKER_COMPOSE) build

# Monitoring
health: ## Check health of services
	@echo "$(GREEN)Checking service health...$(NC)"
	@curl -f http://localhost/health/ && echo "$(GREEN)✓ Web service is healthy$(NC)" || echo "$(RED)✗ Web service is down$(NC)"

# Documentation
api-docs: ## Open API documentation in browser
	@echo "$(GREEN)Opening API documentation...$(NC)"
	@python -m webbrowser http://localhost/api/docs/
