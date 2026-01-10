from fastapi import FastAPI
from src.infrastructure.database import recreate_all
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(application: FastAPI):
    # 啟動時執行
    """
    Run startup tasks and provide the application lifespan context.
    
    Performs database initialization by invoking startup routines (recreates or initializes database state) and then yields control to allow the application to run. If a startup task raises an exception, application startup will fail and the exception will propagate.
    
    Returns:
        A context manager that yields control to the running application after startup tasks complete.
    """
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
    """
    Return a welcome message and the application's running status.
    
    Returns:
        dict: JSON-serializable object with keys "message" (welcome string) and "status" ("running").
    """
    return {
        "message": "Welcome to the CyWeb E-commerce Backend API!",
        "status": "running",
    }


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}