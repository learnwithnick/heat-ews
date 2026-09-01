from fastapi import FastAPI

app = FastAPI(title="heat-engine", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok", "service": "heat-engine"}
