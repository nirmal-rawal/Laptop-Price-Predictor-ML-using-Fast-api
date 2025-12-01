import uvicorn
import asyncio
from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from laptop_price_predictor.core.config import settings
from laptop_price_predictor.services.v1.prediction_service import prediction_service
from laptop_price_predictor.routers.v1._base import base_router
from laptop_price_predictor.core.logger import logger


# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting Laptop Price Predictor API")
    
    try:
        # Initialize prediction service
        await prediction_service.initialize_model()
        
        # Store service in app state
        app.state.prediction_service = prediction_service
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Startup initialization failed: {e}")
        raise
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down Laptop Price Predictor API")
    
    try:
        # Cleanup can be done here if needed
        logger.info("Cleanup completed successfully")
    except Exception as e:
        logger.error(f"Shutdown cleanup failed: {e}")


# Create FastAPI application with lifespan
app = FastAPI(
    title="Laptop Price Predictor API",
    description="Machine Learning API for predicting laptop prices based on specifications with full CRUD operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(base_router, prefix="/api")

# Root endpoint
@app.get("/", tags=["default"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Laptop Price Predictor API",
        "version": "1.0.0",
        "docs": "/docs",
        "health_check": "/api/v1/prediction/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True if settings.app_env == "development" else False,
        log_level="info"
    )