#!/usr/bin/env python3
"""
CosyVoice Web Application
Main FastAPI server serving on port 9080
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from webapp.api.routes import router as api_router
from webapp.config import config

# Create FastAPI app
app = FastAPI(
    title="CosyVoice Web Demo",
    description="Voice Cloning Web Application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main web interface"""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>CosyVoice Web Demo</h1><p>Frontend not yet implemented</p>"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "cosyvoice-web",
        "cosyvoice_api": config.get_cosyvoice_url()
    }

@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "cosyvoice_api_url": config.get_cosyvoice_url(),
        "host": config.HOST,
        "port": config.PORT,
        "debug": config.DEBUG
    }

if __name__ == "__main__":
    print(f"Starting CosyVoice Web Application...")
    print(f"Web Server: http://{config.HOST}:{config.PORT}")
    print(f"CosyVoice API: {config.get_cosyvoice_url()}")
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )
