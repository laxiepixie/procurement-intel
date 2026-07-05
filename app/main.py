from fastapi import FastAPI
from app.routers import leakage, ingestion

app = FastAPI(title="Procurement Intel Core")

app.include_router(leakage.router, prefix="/api/v1")
app.include_router(ingestion.router, prefix="/api/v1")

@app.get("/health")
def system_health():
    """Validasi uptime peladen."""
    return {"status": "operational", "components": ["fastapi", "postgresql_bridge"]}