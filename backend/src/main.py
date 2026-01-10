from fastapi import FastAPI
from src.infrastructure.database import recreate_all
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(application: FastAPI):
    # 啟動時執行
    await recreate_all()
    yield
app = FastAPI(
    title="CyWeb E-commerce Backend",
    description="Modular Monolith API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

@app.get("/api")
async def root():
    return {
        "message": "Welcome to the CyWeb E-commerce Backend API!",
        "status": "running",
    }


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
