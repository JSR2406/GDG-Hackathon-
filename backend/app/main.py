from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import users, items, barter, matches, lost_found, eco_credits
from app.database import engine, Base
import os

# Create Tables on Startup (Essential for Vercel/Mock DB)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="🌍 Eco-Sync API",
    description="AI-Driven Circular Barter Agent for Campus Sustainability",
    version="1.0.0"
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for serving images
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(users.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")
app.include_router(barter.router, prefix="/api/v1")
app.include_router(matches.router, prefix="/api/v1")
app.include_router(lost_found.router, prefix="/api/v1")
app.include_router(eco_credits.router, prefix="/api/v1")

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "🌍 Eco-Sync MVP",
        "status": "online",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "eco-sync-api"}
