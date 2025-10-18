"""
FastAPI Application for Financial Agent
Main entry point for the API server
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
import warnings

warnings.filterwarnings('ignore')

# Create FastAPI app
app = FastAPI(
    title="Financial Agent API",
    description="Multi-agent financial analysis system using LangGraph",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["analysis"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Financial Agent API",
        "version": "3.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.core.config import Config

    config_status = Config.validate_config()

    return {
        "status": "healthy",
        "api_keys_configured": config_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
