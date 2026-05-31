VENV := .venv/bin
PYTHON := $(VENV)/python
RUFF := $(VENV)/ruff
DJLINT := $(VENV)/djlint
DJANGO_UPGRADE := $(VENV)/django-upgrade

.PHONY: check lint format test build

check: lint test build

lint:
	$(RUFF) check .
	npm run check:js
	$(DJLINT) semantic_admin demo --check
	git ls-files '*.py' | xargs $(DJANGO_UPGRADE) --target-version 4.2 --check

format:
	$(RUFF) check . --fix
	npm run fix:js
	$(DJLINT) semantic_admin demo --reformat

test:
	SECRET_KEY=test-secret $(PYTHON) demo/manage.py test --verbosity 1

build:
	uv build
