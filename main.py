from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from src.config import settings
from src.database.mongodb_service import MongoDBService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
mongo_service = MongoDBService(
    connection_string=settings.mongodb_url,
    database_name=settings.mongodb_database
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting Core Behavior Identification Engine...")
    mongo_service.connect()
    yield
    # Shutdown
    logger.info("Shutting down...")
    mongo_service.close()


# Create FastAPI application
app = FastAPI(
    title="Core Behavior Identification Engine",
    description="API for analyzing and clustering user behaviors",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Core Behavior Identification Engine",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": "2025-10-25T09:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
