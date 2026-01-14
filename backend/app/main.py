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


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    from app.services.vector_service import vector_service
    from app.services.llm_service import llm_service
    from app.services.google_drive_service import drive_service
    
    # Initialize vector service with Qdrant credentials
    if settings.QDRANT_URL and settings.QDRANT_API_KEY:
        try:
            vector_service.qdrant_url = settings.QDRANT_URL
            vector_service.qdrant_key = settings.QDRANT_API_KEY
            vector_service._initialize()
            logger.info("✅ Vector service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize vector service: {e}")
    
    # Initialize LLM service with Groq API key
    if settings.GROQ_API_KEY:
        try:
            from groq import Groq
            llm_service.api_key = settings.GROQ_API_KEY
            llm_service.client = Groq(api_key=settings.GROQ_API_KEY)
            logger.info("✅ LLM service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM service: {e}")
    
    # Initialize Google Drive service if credentials provided
    if settings.GOOGLE_DRIVE_CREDENTIALS_PATH:
        try:
            drive_service.credentials_path = settings.GOOGLE_DRIVE_CREDENTIALS_PATH
            drive_service._authenticate()
            logger.info("✅ Google Drive service initialized")
        except Exception as e:
            logger.error(f"⚠️  Google Drive not initialized: {e}")
    
    # Initialize YouTube service with API key
    if settings.YOUTUBE_API_KEY:
        try:
            from app.services.social_media.youtube_service import youtube_service
            youtube_service.api_key = settings.YOUTUBE_API_KEY
            from googleapiclient.discovery import build
            youtube_service.youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
            logger.info("✅ YouTube service initialized with API key")
        except Exception as e:
            logger.error(f"⚠️  YouTube service not initialized: {e}")


# Import API routers
from app.api import news, social, sentiment, chat, documents

# Register routers
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(social.router, prefix="/api/social", tags=["social"])
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["sentiment"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

