# AZI Backend — local dev tasks.
# Usage: `make <target>` from the backend/ directory. Run `make help` for a list.

# Use the project virtualenv without needing to `source` it.
VENV        := .venv
PY          := $(VENV)/bin/python
PIP         := $(VENV)/bin/pip
UVICORN     := $(VENV)/bin/uvicorn
PG_CTL      := brew services
HOST        ?= 127.0.0.1
PORT        ?= 8000

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

# --- one-time setup -------------------------------------------------------

.PHONY: setup
setup: venv env db-start db-create init-db seed ## Full first-time setup (venv, .env, db, tables, admin)
	@echo "Setup complete. Run 'make run' to start the app."

.PHONY: venv
venv: ## Create the virtualenv and install dependencies
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

.PHONY: env
env: ## Create .env from the example if it does not exist
	@test -f .env || (cp .env.example .env && echo "Created .env from .env.example")

# --- database -------------------------------------------------------------

.PHONY: db-start
db-start: ## Start the local PostgreSQL server
	$(PG_CTL) start postgresql@14

.PHONY: db-stop
db-stop: ## Stop the local PostgreSQL server
	$(PG_CTL) stop postgresql@14

.PHONY: db-create
db-create: ## Create the azi_db database (idempotent)
	@createdb azi_db 2>/dev/null && echo "Created azi_db" || echo "azi_db already exists"

.PHONY: init-db
init-db: ## Create all tables in the configured database
	$(PY) -m scripts.init_db

.PHONY: seed
seed: ## Seed the superAdmin login user (superadmin@gmail.com / Welcome@1234)
	$(PY) -m scripts.seed_superadmin

.PHONY: db-shell
db-shell: ## Open a psql shell on azi_db
	psql "postgresql://postgres:postgres@localhost:5432/azi_db"

.PHONY: db-reset
db-reset: ## Drop and recreate azi_db, then re-init tables and seed admin
	@dropdb --if-exists azi_db
	@createdb azi_db && echo "Recreated azi_db"
	$(PY) -m scripts.init_db
	$(PY) -m scripts.seed_superadmin

# --- run ------------------------------------------------------------------

.PHONY: run
run: ## Run the app with auto-reload (http://127.0.0.1:8000/docs)
	$(UVICORN) main:app --reload --host $(HOST) --port $(PORT)

.PHONY: serve
serve: ## Run the app without reload (production-like)
	$(UVICORN) main:app --host $(HOST) --port $(PORT)

# --- quality --------------------------------------------------------------

.PHONY: test
test: ## Run the test suite (needs a test database)
	$(PY) -m pytest

.PHONY: lint
lint: ## Lint with ruff
	$(VENV)/bin/ruff check .

.PHONY: fmt
fmt: ## Format with black and apply ruff autofixes
	$(VENV)/bin/black .
	$(VENV)/bin/ruff check --fix .

.PHONY: schema
schema: ## Regenerate schema.sql from the models
	$(PY) -m scripts.dump_schema > schema.sql
