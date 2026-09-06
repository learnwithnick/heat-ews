from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

from app.physics.wbgt import wbgt_from_weather

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


class WeatherPoint(BaseModel):
    t2m: float
    rh: float
    wind10m: float
    dni: float
    diffuse: float
    pressure_hpa: float
    lat_deg: float
    lon_deg: float
    when_utc: datetime


class WbgtResult(BaseModel):
    wbgt: float


@app.post("/compute/batch")
def compute_batch(points: list[WeatherPoint]) -> list[WbgtResult]:
    results = []
    for p in points:
        value = wbgt_from_weather(
            p.t2m,
            p.rh,
            p.wind10m,
            p.dni,
            p.diffuse,
            p.pressure_hpa,
            p.lat_deg,
            p.lon_deg,
            p.when_utc,
        )
        results.append(WbgtResult(wbgt=value))
    return results

