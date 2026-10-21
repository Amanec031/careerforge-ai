# CareerForge AI

Resume tailoring (LaTeX to PDF) and job alerts. **This is Checkpoint 1 of 5: the foundation.**

## Verification status (read this)
Written in a sandbox with no network or Docker, so I could only check that the Python
files compile and the YAML parses. **Not yet run:** Docker build, migrations, pytest, ruff, mypy.
Run the steps below and tell me any error output; I will fix it before Checkpoint 2.

## Bazzite (Fedora Atomic) setup

1. Check what you have (read-only, safe):
   ```bash
   docker --version; docker compose version
   podman --version; podman compose version
   ```
   Bazzite ships **Podman**. If `docker` is missing, use Podman (below). To see whether Bazzite
   offers a Docker helper: `ujust --list | grep -i docker`.
2. Using Podman: `systemctl --user enable --now podman.socket`, and if `podman compose`
   is missing, install it in a toolbox/distrobox or via `pip install --user podman-compose`.
   Then use `make ... COMPOSE="podman compose"` (or `podman-compose`) for every command below.
3. Clone and configure:
   ```bash
   git clone <your-private-repo-url> careerforge-ai && cd careerforge-ai
   cp .env.example .env
   sed -i "s/generate-with-openssl-rand-hex-32/$(openssl rand -hex 32)/" .env
   ```
   Edit `.env`: set `POSTGRES_PASSWORD` and use the same password inside `DATABASE_URL`.
4. Start: `make up` (builds images; starts db, redis, backend, worker, scheduler).
5. Migrate: `make migrate`  (creates all tables).
6. Verify: `curl localhost:8000/health` then `curl localhost:8000/health/ready`
   (ready = DB and Redis reachable). API docs: http://localhost:8000/docs
7. Test and lint: `make test` and `make lint`.
8. Day to day: `make logs`, `make down`, `make backup` (writes SQL dump to `backups/`),
   update with `git pull && make up && make migrate`.

Troubleshooting: port 5432/8000 busy, stop the other service; permission denied on bind
mounts means SELinux, the compose file already uses `:z`; `docker compose ps` shows health.

## Windows / generic Linux
Install Docker Desktop (Windows) or Docker Engine + compose plugin (Linux), then the same
`make` targets (Windows: run the `docker compose ...` commands from the Makefile directly).

## Layout
`backend/` FastAPI + SQLAlchemy + Alembic + Celery app | `docs/` architecture |
`.github/workflows/ci.yml` lint, types, tests, migration check | `frontend/`, `latex-service/`,
`worker/`, `shared/` reserved for later checkpoints.
