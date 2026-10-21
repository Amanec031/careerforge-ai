# Override for Podman:  make up COMPOSE="podman compose"
COMPOSE ?= docker compose

up:        ; $(COMPOSE) up -d --build
down:      ; $(COMPOSE) down
logs:      ; $(COMPOSE) logs -f --tail=100
migrate:   ; $(COMPOSE) exec backend alembic upgrade head
test:      ; $(COMPOSE) exec backend pytest -q
lint:      ; $(COMPOSE) exec backend sh -c "ruff check . && mypy app"
psql:      ; $(COMPOSE) exec db psql -U $${POSTGRES_USER:-careerforge} -d $${POSTGRES_DB:-careerforge}
backup:    ; mkdir -p backups && $(COMPOSE) exec -T db pg_dump -U $${POSTGRES_USER:-careerforge} $${POSTGRES_DB:-careerforge} > backups/db-$$(date +%F-%H%M).sql
