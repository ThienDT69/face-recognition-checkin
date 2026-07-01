from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api.v1 import employees, recognition, checkin, auth
from app.services.face_recognition import FaceRecognitionService
from app.db.database import engine, Base

settings = get_settings()

# Initialize face recognition service at startup
face_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting Face Recognition Check-in System...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Initialize face recognition model
    global face_service
    face_service = FaceRecognitionService(model_name=settings.FACE_MODEL)
    print(f"✅ Face Recognition Model loaded: {settings.FACE_MODEL}")
    
    # Create upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    print(f"✅ Upload directory created: {settings.UPLOAD_DIR}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Face Recognition Check-in System...")
    if face_service:
        face_service.cleanup()

app = FastAPI(
    title=settings.APP_NAME,
    description="Face Recognition Based Check-in System",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# API routes
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(employees.router, prefix=settings.API_V1_STR, tags=["employees"])
app.include_router(recognition.router, prefix=settings.API_V1_STR, tags=["recognition"])
app.include_router(checkin.router, prefix=settings.API_V1_STR, tags=["checkin"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Face Recognition Check-in System",
        "docs": "/docs",
        "version": settings.APP_VERSION
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "app": settings.APP_NAME
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
