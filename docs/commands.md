# Commands

## Tests

Run the whole test suite (works with or without `python -m`, thanks to `pyproject.toml`):

    pytest -v

Run one test file:

    pytest tests/test_health.py -v

Prove the tests ignore the shell environment:

    SECRET_KEY=anything APP_ENV=production pytest -v

## Run the app locally

    flask --app app.app run
    curl -i http://127.0.0.1:5000/health
