CREATE TABLE forecast_grid_hourly (
    id            BIGSERIAL PRIMARY KEY,
    run_time      TIMESTAMPTZ NOT NULL,
    valid_time    TIMESTAMPTZ NOT NULL,
    lat           DOUBLE PRECISION NOT NULL,
    lon           DOUBLE PRECISION NOT NULL,
    t2m           REAL,
    rh            REAL,
    pressure_hpa  REAL,
    wind10m       REAL,
    dni           REAL,
    diffuse       REAL,
    cloud_cover   REAL,
    CONSTRAINT uq_forecast_point UNIQUE (run_time, valid_time, lat, lon)
);

CREATE INDEX idx_forecast_valid_time ON forecast_grid_hourly (valid_time);

