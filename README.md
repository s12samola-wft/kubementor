# KubeMentor

KubeMentor is a hands-on Kubernetes learning platform and a DevOps portfolio project. The application will teach Kubernetes step by step, and its own infrastructure is built with the same tools and practices it teaches.

## Current status

KubeMentor is currently a small Flask web service with health and readiness endpoints and environment-based configuration. Containers, CI, Kubernetes, and monitoring are planned and will be added milestone by milestone.

| Endpoint  | Purpose                          | Response                          |
|-----------|----------------------------------|-----------------------------------|
| `/`       | Home page                        | `Welcome to KubeMentor`           |
| `/health` | Liveness: is the process alive?  | `{"status": "healthy"}`, HTTP 200 |
| `/ready`  | Readiness: can it serve traffic? | `{"status": "ready"}`, HTTP 200   |

## Run locally

Requires Python 3.12.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

flask --app app.app run
curl http://127.0.0.1:5000/health
```

## Configuration

Configuration is read from environment variables when the application starts.

| Variable     | Values                                       | Default       | Notes                                  |
|--------------|----------------------------------------------|---------------|----------------------------------------|
| `APP_ENV`    | `development`, `testing`, `production`       | `development` | Unknown values stop the app at startup |
| `SECRET_KEY` | any string                                   | none          | Required in `production`               |

The application fails fast: it refuses to start with an unknown `APP_ENV`, or in production without a `SECRET_KEY`. Never commit real secrets; supply them at runtime.

## Tests

```bash
pytest
```

The tests always use the testing configuration, so they give the same result whatever is set in your shell.

## Project layout

```text
app/
  __init__.py      create_app() application factory
  config.py        development, testing, and production settings
  app.py           application object for `flask run` and WSGI servers
  routes/main.py   blueprint with /, /health, /ready
tests/             pytest suite and shared fixtures
docs/              engineering journal and command notes
```

## Roadmap

Docker image, CI pipeline with image scanning, PostgreSQL, Kubernetes on Minikube, Helm, Argo CD (GitOps), TLS with cert-manager, monitoring with Prometheus, Grafana, and Loki, alerting to Slack, network policies and RBAC, and finally a low-cost production cluster.
