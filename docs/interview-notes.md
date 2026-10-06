# KubeMentor — Interview Notes

The short, polished version of the project story, for reading before an interview.
The full record lives in `docs/Kubementor_journal`.

Rule: only claim what is built and committed. Update this file at the end of every stage.

Last updated: 2026-10-06 (stage: Docker image done, architecture documented; next: Jenkins CI)

---

## 1. Project pitch (30 seconds)

> I'm building KubeMentor, a Kubernetes learning platform, as a hands-on DevOps project. So far I've built the Python Flask service with health and readiness endpoints, environment-based configuration that fails fast when a production secret is missing, and an automated pytest suite that gives the same result in any environment. I've packaged it as a hardened Docker image: base image pinned by digest, hash-locked dependencies installed as wheels only, gunicorn, and a non-root user, with the secret injected at runtime. I work in feature branches with reviewed PRs, test every stage with a deliberate failure drill, and keep an engineering journal of every problem I hit. Next is a Jenkins pipeline with Trivy image scanning, then Kubernetes with Argo CD and monitoring with Prometheus and Grafana.

## 2. What is built so far

| Area | What exists | Why it matters for operations |
|---|---|---|
| Application | Flask app with `/`, `/health`, `/ready` | `/health` and `/ready` will become Kubernetes liveness and readiness probes |
| Structure | Application factory (`create_app`) and blueprints | One app, many configurations: dev, testing, production |
| Configuration | `APP_ENV` chooses the config; `SECRET_KEY` required in production | The app crashes at startup with a clear message instead of running insecurely |
| Testing | 7 pytest tests, including the configuration rules | Tests will be the first gate in the CI pipeline |
| Dependencies | `.in` files compiled by `uv` into lock files with sha256 hashes | A tampered or swapped package fails the build instead of shipping |
| Container | Dockerfile: base pinned by digest, gunicorn, non-root user (uid 10001), patched OS package | Reproducible, least-privilege image; secret supplied at runtime, never baked in |
| Smoke test | `scripts/check_health.py [base_url]`, exit code 0/1 | Usable as a CI or post-deploy check |
| Documentation | README, `docs/architecture.md` with diagrams, engineering journal | Anyone can run, understand, and review the project |
| Workflow | Git feature branches, PRs, small commits, failure drills | Traceable history; every change can be explained |

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

### Story 6 — `git push` rejected with HTTP 403

- **Situation:** Pushing my first feature branch to GitHub failed with HTTP 403, even though I was the owner of the repository.
- **Task:** Find out why GitHub refused me and fix it without weakening security.
- **Action:** I checked how Git was authenticating. Git's `store` credential helper was sending a saved token, and that token was read-only, so GitHub accepted who I was but refused the write. The token was also saved in plain text on disk. I switched the remote to SSH (`git@github.com:...`) and logged the GitHub CLI in separately for pull requests.
- **Result:** Pushes work over SSH, and no token sits in plain text for Git.
- **Learned:** 403 means "I know who you are, but you are not allowed"; 401 means "I don't know who you are". When a push fails, check which credential is actually being sent and what permissions it has, before changing repository settings.

### Story 7 — Proving the dependency lock actually protects the build

- **Situation:** I locked every Python dependency with sha256 hashes and made the Docker build install wheels only (`pip --require-hashes --only-binary :all:`). I needed proof that this stops a tampered package.
- **Task:** Run a failure drill: break it on purpose, watch it fail, fix it, verify.
- **Action:** I changed one character of a hash in `requirements.txt` and rebuilt. pip stopped the build with `THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE`, showing expected vs got. I reverted the change and the build passed. When re-checking, I found that changing the *other* hash of the same package did **not** break the build. Each package lists a hash for the wheel and one for the source archive; pip accepts any listed hash, and with `--only-binary` it only ever downloads the wheel, so the source-archive hash is never compared.
- **Result:** The control works for what is actually installed. I also verified every hash against PyPI's published values, recompiled the lock files to confirm they match `requirements.in`, and rebuilt with `--no-cache`, because a cached build never re-runs pip.
- **Learned:** A drill has to break the thing that is really used. "I changed something and it still passed" is a signal to find out what is being checked, not a reason to assume the protection is broken, or that it works.

### Story 8 — Docker "could not be found" while Docker was running

- **Situation:** Docker Desktop was running, but every `docker` command in WSL printed `The command 'docker' could not be found in this WSL 2 distro`.
- **Task:** Work out whether the engine was down or just unreachable.
- **Action:** `docker.exe version` (the Windows client) returned the server version, so the engine was up. `type -a docker` showed that WSL was running Docker Desktop's placeholder script, and the real client link `/usr/bin/docker` was missing. Re-enabling the distro under Docker Desktop → Settings → Resources → WSL integration fixed it.
- **Result:** `docker version` showed the server again, and the README quick start passed exactly as written.
- **Learned:** "Service running" and "service reachable from where I am" are different questions. Check which binary actually runs before restarting things.

## 4. Tools: what I used and the alternatives

| Purpose | Used in KubeMentor | Alternatives seen in companies |
|---|---|---|
| Web framework | Flask | Django, FastAPI |
| Testing | pytest | unittest |
| Version control | Git + GitHub, feature branches, SSH auth | GitLab, Bitbucket; trunk-based development |
| Dependency locking | uv (`uv pip compile --generate-hashes`) | pip-tools, Poetry |
| Containers | Docker, gunicorn | Podman; uvicorn; Kaniko for in-cluster builds |
| Diagrams | Mermaid in Markdown (rendered by GitHub) | draw.io, Excalidraw, Lucidchart |

Planned, not yet built: Jenkins, Trivy, PostgreSQL, Kubernetes (Minikube, then k3s), Helm, Argo CD, cert-manager, Calico, Prometheus, Grafana, Loki, Alertmanager with Slack, OpenTofu.

## 5. Questions I can answer now

- **Liveness vs readiness?** Liveness asks "is the process alive?" — if it fails, Kubernetes restarts the container. Readiness asks "can it serve traffic right now?" — if it fails, the Pod is removed from the Service but not restarted.
- **Why fail fast on a missing secret?** A crash at startup with a clear message is easy to spot and fix. An app running without its secret fails later, quietly, and possibly insecurely.
- **Why must tests not depend on the environment?** CI runners, containers, and laptops all have different environments. A test result should reflect the code, not the machine.
- **Collection error vs test failure?** A collection error means pytest could not load the test file, so nothing ran. A failure means the test ran and the result did not match the expectation.
- **Why feature branches?** `main` stays stable; work is reviewed and tested before it is merged.
- **Why pin the base image by digest?** A tag such as `python:3.12-slim` can point to a different image tomorrow; a digest cannot. Updates become a deliberate, reviewed change.
- **Why run the container as non-root?** If the app is compromised, the attacker has fewer permissions, and many Kubernetes clusters refuse root containers.
- **Why not put the secret in the image?** Anyone who can pull the image could read it, and changing it would mean rebuilding. It is injected at runtime instead.
- **What does `--require-hashes` protect against?** A package on the index being replaced or tampered with: pip refuses any file whose hash is not in the lock file.
- **Why rebuild with `--no-cache` when testing the build?** Cached layers are reused without running their commands, so a cached build proves nothing about steps that did not run.
