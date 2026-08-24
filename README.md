# URL Shortener — Hands-On System Design Learning Project

A URL shortener built **from scratch**, phase by phase, to build real intuition
for distributed systems concepts (not just to produce working code).

Mentor model: Senior Staff / Distributed Systems Architect.
See `docs/` for the design journey — each numbered doc corresponds to a phase.

## Progress

- [x] Phase 0 — Requirements & capacity estimation (`docs/01-requirements.md`)
- [ ] Phase 1 — Simplest working system (FastAPI + PostgreSQL)
- [ ] Phase 2 — Database design & indexing
- [ ] Phase 3 — Short code generation (Base62, sequential IDs)
- [ ] Phase 4 — Alternative ID generation strategies
- [ ] Phase 5 — Concurrency & race conditions
- [ ] Phase 6 — Redis cache (cache-aside)
- [ ] Phase 7 — Cache concepts (stampede, invalidation, TTL)
- [ ] Phase 8 — Cache failure & graceful degradation
- [ ] Phase 9 — Rate limiting
- [ ] Phase 10 — Analytics (sync vs async)
- [ ] Phase 11 — Kafka
- [ ] Phase 12 — Observability (Prometheus/Grafana)
- [ ] Phase 13 — Distributed tracing (OpenTelemetry)
- [ ] Phase 14 — Load testing (Locust)
- [ ] Phase 15 — Horizontal scaling
- [ ] Phase 16 — Database scaling
- [ ] Phase 17 — Failure engineering
- [ ] Phase 18 — Security
- [ ] Phase 19 — Production architecture
- [ ] Phase 20 — Mock system design interview

## Stack

Python 3.12+, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Redis, Kafka (later),
pytest, Locust, Prometheus/Grafana, OpenTelemetry, Docker Compose.

Kubernetes is intentionally deferred until the single-machine / Docker-based
system is fully understood.

## Quickstart (updated as phases land)

```bash
make venv && source .venv/bin/activate
make install
make up        # starts PostgreSQL
make run        # starts the API (from Phase 1 onward)
make test
```
