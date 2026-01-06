from fastapi import FastAPI

app = FastAPI(
    title="CyWeb E-commerce Backend",
    description="Modular Monolith API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

@app.get("/api")
async def root():
    return {
        "message": "Welcome to the CyWeb E-commerce Backend API!",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok"
    }