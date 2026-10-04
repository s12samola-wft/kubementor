# KubeMentor — Interview Notes

The short, polished version of the project story, for reading before an interview.
The full record lives in `docs/Kubementor_journal`.

Rule: only claim what is built and committed. Update this file at the end of every stage.

Last updated: 2026-10-04 (stage: application foundation and configuration)

---

## 1. Project pitch (30 seconds)

> I'm building KubeMentor, a Kubernetes learning platform, as a hands-on DevOps project. So far I've built the Python Flask service with health and readiness endpoints, environment-based configuration that fails fast when a production secret is missing, and an automated pytest suite that gives the same result in any environment. I work in feature branches with reviewed commits and keep an engineering journal of every problem I hit. Next I'm containerising it with Docker, adding a Jenkins pipeline with Trivy image scanning, then deploying to Kubernetes with Argo CD and monitoring it with Prometheus and Grafana.

## 2. What is built so far

| Area | What exists | Why it matters for operations |
|---|---|---|
| Application | Flask app with `/`, `/health`, `/ready` | `/health` and `/ready` will become Kubernetes liveness and readiness probes |
| Structure | Application factory (`create_app`) and blueprints | One app, many configurations: dev, testing, production |
| Configuration | `APP_ENV` chooses the config; `SECRET_KEY` required in production | The app crashes at startup with a clear message instead of running insecurely |
| Testing | 7 pytest tests, including the configuration rules | Tests will be the first gate in the CI pipeline |
| Workflow | Git feature branches, small commits, engineering journal | Traceable history; every change can be explained |

## 3. Challenges I solved (STAR stories)

### Story 1 — Tests that depended on my shell

- **Situation:** My tests passed on my laptop, but I suspected they depended on environment variables in my shell, which would make CI unreliable.
- **Task:** Prove it, and make the tests give the same result anywhere.
- **Action:** I reproduced it by running `APP_ENV=production python -m pytest -v`. Two tests failed with `RuntimeError: SECRET_KEY must be provided in production`. Reading the traceback, I saw `config_name = 'production'`: the tests called `create_app()` without choosing a configuration, so they inherited whatever the environment had. I changed them to always use the testing configuration and added tests for the fail-fast rules.
- **Result:** The suite passes even with `APP_ENV=production` and `SECRET_KEY` set in the shell.
- **Learned:** The application was behaving correctly; the tests were not isolated. Separate the symptom (failing tests) from the root cause (hidden dependency on the environment).

### Story 2 — A variable that "wasn't there"

- **Situation:** After the drill above, `echo $APP_ENV` still printed `production`, yet Python behaved as if it was not set.
- **Action:** I checked `history` and found I had earlier run `APP_ENV=production` on its own line.
- **Root cause:** That creates a shell variable, which child processes such as Python never see. Only `export` makes an environment variable that programs inherit. `VAR=value command` sets it for one command only.
- **Learned:** This is why containers and Pods only see variables that are explicitly passed into their environment, for example through `env:` in a Kubernetes manifest.

### Story 3 — Configuration read at startup, not at runtime

- **Situation:** A test set `SECRET_KEY` with `monkeypatch.setenv`, but the app still reported it missing.
- **Root cause:** `app/config.py` reads `SECRET_KEY` once, when the module is imported. The test set the variable after that moment.
- **Action:** I patched the configuration class directly in the test, and kept the application code unchanged because in real use the environment is always set before the process starts.
- **Learned:** Configuration is fixed at process start. In Kubernetes, updating a Secret does not change a running Pod until it restarts, which is why tools like Stakater Reloader exist.

### Story 4 — Port 5000 already in use

- **Situation:** Restarting the Flask server failed with `Address already in use`.
- **Root cause:** I had pressed `Ctrl+Z`, which suspends a process rather than stopping it, so it still held port 5000.
- **Action:** `jobs` showed the stopped process; `fg %1` then `Ctrl+C` terminated it.
- **Learned:** `Ctrl+C` terminates, `Ctrl+Z` suspends. A port conflict means some process still owns the port, so find the process before changing anything.

### Story 5 — pytest could not import the app

- **Situation:** Running `pytest` failed with `ModuleNotFoundError: No module named 'app'`, and pytest reported `collected 0 items / 1 error`.
- **Root cause:** pytest's import path did not include the project root. `python -m pytest` worked because it adds the current directory to the path.
- **Action:** Short term I used `python -m pytest`; later I added `pythonpath = ["."]` to `pyproject.toml` so plain `pytest` works everywhere, including CI.
- **Learned:** A collection error means the tests never ran, which is different from a test failure. Fix it by tracing the import chain, not by editing the tests.

## 4. Tools: what I used and the alternatives

| Purpose | Used in KubeMentor | Alternatives seen in companies |
|---|---|---|
| Web framework | Flask | Django, FastAPI |
| Testing | pytest | unittest |
| Version control | Git + GitHub, feature branches | GitLab, Bitbucket; trunk-based development |

Planned, not yet built: Docker, Jenkins, Trivy, PostgreSQL, Kubernetes (Minikube, then k3s), Helm, Argo CD, cert-manager, Calico, Prometheus, Grafana, Loki, Alertmanager with Slack, OpenTofu.

## 5. Questions I can answer now

- **Liveness vs readiness?** Liveness asks "is the process alive?" — if it fails, Kubernetes restarts the container. Readiness asks "can it serve traffic right now?" — if it fails, the Pod is removed from the Service but not restarted.
- **Why fail fast on a missing secret?** A crash at startup with a clear message is easy to spot and fix. An app running without its secret fails later, quietly, and possibly insecurely.
- **Why must tests not depend on the environment?** CI runners, containers, and laptops all have different environments. A test result should reflect the code, not the machine.
- **Collection error vs test failure?** A collection error means pytest could not load the test file, so nothing ran. A failure means the test ran and the result did not match the expectation.
- **Why feature branches?** `main` stays stable; work is reviewed and tested before it is merged.
