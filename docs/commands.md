# Commands

## Tests

Run the whole test suite (works with or without `python -m`, thanks to `pyproject.toml`):

    pytest -v

Run one test file:

    pytest tests/test_health.py -v

Prove the tests ignore the shell environment:

    SECRET_KEY=anything APP_ENV=production pytest -v

## Lint

Ruff is pinned in `requirements-dev.in`; its rules are listed in `pyproject.toml`. CI runs exactly these two commands:

    ruff check .
    ruff format --check .

Auto-fix what can be fixed safely, and reformat:

    ruff check --fix .
    ruff format .

## Dependencies

Top-level packages live in `requirements.in` and `requirements-dev.in`. The `.txt` files are generated lock files: every package pinned with hashes. Never edit the `.txt` files by hand.

Change a version or add a package: edit the `.in` file, then regenerate both locks:

    uv pip compile requirements.in --python-version 3.12 --generate-hashes --no-header -o requirements.txt
    uv pip compile requirements-dev.in --python-version 3.12 --generate-hashes --no-header -o requirements-dev.txt

Install exactly what is locked:

    pip install --require-hashes --only-binary :all: -r requirements-dev.txt

## Run the app locally

    flask --app app.app run
    curl -i http://127.0.0.1:5000/health
