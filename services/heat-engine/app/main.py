from fastapi import FastAPI
from pydantic import BaseModel

from app.physics.heat_index import heat_index_c

app = FastAPI(title="heat-engine", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "heat-engine"}


class HeatIndexRequest(BaseModel):
    temp_c: float
    rh: float


class HeatIndexResponse(BaseModel):
    heat_index_c: float


@app.post("/compute/heat-index", response_model=HeatIndexResponse)
def compute_heat_index(req: HeatIndexRequest):
    return HeatIndexResponse(heat_index_c=heat_index_c(req.temp_c, req.rh))
