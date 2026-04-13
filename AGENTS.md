## Setup

Install development dependencies:

```bash
uv sync --group dev
```

## Checks

Run Python lint:

```bash
uv run ruff check .
```

Run JavaScript lint/format checks:

```bash
npm ci
npm run check:js
```

Run Django template lint:

```bash
uv run djlint semantic_admin demo --check
```

Run Django upgrade compatibility check against the minimum supported version:

```bash
git ls-files '*.py' | xargs uv run django-upgrade --target-version 4.2 --check
```

Run the package test suite:

```bash
SECRET_KEY=test-secret uv run python demo/manage.py test semantic_admin.tests
```

Run the full Django test suite:

```bash
SECRET_KEY=test-secret uv run python demo/manage.py test
```
