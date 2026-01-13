"""
GovGPT - AI-Powered Government Data Analysis Platform
Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.config import settings

# Configure logging
logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="GovGPT API",
    description="AI-powered government data analysis and decision support platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting GovGPT API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    # TODO: Initialize vector DB connection
    # TODO: Initialize LLM client
    # TODO: Load embedding model


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down GovGPT API")
    # TODO: Close connections


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "GovGPT API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "services": {
                "api": "operational",
                # TODO: Add actual service checks
                "database": "pending",
                "vector_db": "pending",
                "llm": "pending"
            }
        }
    )


# TODO: Import and include routers when implemented
# from app.api import chat, documents, analysis
# app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
# app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
# app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
