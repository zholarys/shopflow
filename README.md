# ShopFlow — Full-Stack E-Commerce DevOps Project

A production-ready e-commerce platform built to demonstrate real-world DevOps practices.

## Architecture

- React Frontend + FastAPI Backend
- PostgreSQL (database) + Redis (caching)
- Nginx as reverse proxy
- Prometheus + Grafana + Loki (monitoring & logging)
- GitHub Actions (CI/CD)
- Docker Compose (orchestration)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite |
| Backend | FastAPI, SQLAlchemy |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Proxy | Nginx |
| Monitoring | Prometheus, Grafana, Loki |
| CI/CD | GitHub Actions |
| Containers | Docker, Docker Compose |

## Features

- JWT authentication (register/login)
- Product catalog with search and category filter
- Shopping cart and orders
- Redis caching — handles 1000+ concurrent users
- Real-time log monitoring via Loki + Grafana
- Automated CI/CD pipeline with tests

## Load Testing Results

| Scenario | Users | Error Rate | p95 Response |
|----------|-------|------------|--------------|
| Without cache | 1000 | 31% | 3.26s |
| With Redis cache | 1000 | 0.48% | 229ms |

## Quick Start

    git clone https://github.com/zholarys/shopflow
    cd shopflow
    cp .env.example .env
    docker compose up -d

Open http://localhost

## CI/CD Pipeline

Every push to main triggers:
1. Backend unit tests (pytest)
2. Frontend lint (ESLint)
3. Docker image build
4. Failed tests block deployment

## Monitoring

- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Loki logs: http://localhost:3100

## Load Testing

    k6 run k6/load_test.js
    k6 run k6/stress_test.js
