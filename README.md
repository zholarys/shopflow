# ShopFlow — DevOps learning project

A local e-commerce demo combining React, FastAPI, PostgreSQL, Redis, Nginx, Prometheus, Grafana and Loki/Alloy. This is a portfolio lab, not a production-ready payment system.

## Start from a fresh clone

Requires Docker Engine, Docker Compose v2+ and a host with enough resources for the full monitoring stack. Ports 80, 3000, 9090, 3100, 6379, 5433 and 8000 must be available on loopback.

```bash
git clone https://github.com/zholarys/shopflow
cd shopflow
cp .env.example .env
# Edit .env: replace all example passwords and SECRET_KEY.
# Generate a JWT key with: openssl rand -hex 32
docker compose up --build -d postgres redis backend
docker compose exec -T backend python -m app.init_db
docker compose exec -T backend python -m app.seed
docker compose up --build -d
curl --fail http://localhost/api/health
```

Open http://localhost. Register a user before placing an order. Re-running the seed command skips existing demo products by name. `init_db` creates missing tables but is not a schema migration system.

## Authentication and application limits

JWTs are checked on order endpoints. Orders belong to the authenticated user and listing is restricted to that user. Creating products requires an admin account; registration creates ordinary users. Order quantities must be positive and duplicate products are aggregated. PostgreSQL row locks serialize stock changes inside the order transaction.

Payments are mocked. Money is still represented as floating point, and product-cache invalidation uses a 60-second TTL. This project needs proper decimal money handling, migrations, cache invalidation, rate limits, backups and operational hardening before production use. `/api/health` checks the HTTP process, not database/Redis readiness.

## Monitoring and logs

- Grafana: http://localhost:3000 (admin and the password from `.env`)
- Prometheus: http://localhost:9090
- Loki API: http://localhost:3100 (not a standalone web UI)

Prometheus and Loki data sources are provisioned in Grafana. In Explore, select Loki and query `{project="shopflow",service="backend"}`. Alloy reads this Compose project's container logs. Access to Docker socket is powerful even with a read-only mount; this is a local lab configuration. A one-shot init container sets the Loki volume owner, and Loki retention is configured for seven days (deletion is asynchronous).

All published ports default to loopback. `HTTP_BIND_ADDRESS` can expose the HTTP proxy on a server; configure TLS and firewall rules before making it public. The backend image runs without root and without development auto-reload.

## CI and checks

GitHub Actions runs backend tests, frontend lint, and Docker image builds. It does not publish images or deploy them; a failed check blocks the build job, not a deployment system.

```bash
cd frontend
npm ci
npm run lint
npm run build
```

Backend tests include authorization, ownership and input-validation regression checks. See the workflow for test environment variables and dependencies.

## Load testing

```bash
k6 run k6/load_test.js
k6 run --summary-export=stress-results.json k6/stress_test.js
```

These scripts exercise catalog and health requests, not a complete authenticated checkout workload. Prior latency/error figures are not presented as reproducible benchmarks: record host resources, commit, cache state, dataset and k6 output for any new comparison.

## Stop

`docker compose down` preserves volumes. `docker compose down -v` (also `make clean`) permanently deletes the lab databases, Grafana state and stored logs.
