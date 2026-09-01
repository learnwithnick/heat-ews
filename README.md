# heat-ews

Ward-level heat stress early warning system. Ingests weather data,
computes heat indices per ward, and issues alerts before dangerous
conditions occur.

## Stack

- PostgreSQL 16 + PostGIS 3.4 — spatial data store
- Redis 7 — cache
- Spring Boot (Java 21) — ingest API
- FastAPI (Python 3.11) — heat-engine compute service

## Prerequisites

- Docker Desktop
- Java 21 (via SDKMAN)
- Python 3.11
- GDAL (for data-prep work)

## Setup

Clone and start the infrastructure:

    git clone https://github.com/learnwithnick/heat-ews.git
    cd heat-ews
    docker compose up -d

Verify both containers are healthy:

    docker compose ps

Set up the heat-engine service:

    cd services/heat-engine
    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Run it:

    uvicorn app.main:app --reload --port 8001

Check it responds:

    curl localhost:8001/health

Interactive API docs: http://localhost:8001/docs

## Services

| Service | Port | Notes |
|---------|------|-------|
| PostGIS | 5432 | db `heatews`, user `heat` |
| Redis | 6379 | cache, no persistence |
| heat-engine | 8001 | FastAPI compute service |

## Repository layout

    infra/                  infrastructure config
    services/ingest-api/    Spring Boot service
    services/heat-engine/   FastAPI compute service
    data-prep/              shapefile → PostGIS loading scripts
    web/                    frontend
    docs/                   documentation
