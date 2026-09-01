CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE ingest_log (
    id          BIGSERIAL PRIMARY KEY,
    source      TEXT NOT NULL,
    run_time    TIMESTAMPTZ NOT NULL DEFAULT now(),
    status      TEXT NOT NULL,
    rows_loaded INTEGER,
    latency_ms  INTEGER
);
