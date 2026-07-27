from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.endpoints import router as api_router
from backend.app.db.init_db import init_db

# Ensure database tables are created on module import/startup
init_db(seed_data=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan events."""
    init_db(seed_data=False)
    yield


app = FastAPI(
    title="AIVOA Customer Complaint Management API",
    description="Enterprise AI Copilot and Complaint Processing Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev/production integration
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API router
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "AIVOA Customer Complaint Management API is operational",
        "docs_url": "/docs",
        "health_check": "/api/health",
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "AIVOA Backend API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
