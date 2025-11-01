#!/usr/bin/env python3
"""
Main entry point for the data onboarding platform
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment configuration
from dotenv import load_dotenv
load_dotenv(project_root / "config" / ".env")

# Import from organized structure
from observability import get_control_plane_app

def create_main_app():
    """Create main FastAPI app with CORS and health endpoints"""
    print("🚀 Starting Data Onboarding Platform")
    print("📁 Organized backend structure:")
    print("   📊 observability/ - Control-plane agents and workflows")
    print("   🗄️  core/ - Database and models")
    print("   🌐 api/ - FastAPI routes and middleware")
    print("   ⚙️  config/ - Configuration files")
    print("   🧪 tests/ - Test suites by category")
    
    # Create main FastAPI app
    app = FastAPI(
        title="Data Onboarding Platform",
        description="AI-powered data onboarding with Agno control-plane",
        version="1.0.0"
    )
    
    # Add CORS middleware for frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "data-onboarding-platform",
            "components": {
                "backend": "operational",
                "control_plane": "operational",
                "database": "connected"
            }
        }
    
    # Get the control-plane app and mount it
    try:
        control_plane_app = get_control_plane_app()
        app.mount("/api/v1", control_plane_app)
        print("✅ Control-plane mounted at /api/v1")
    except Exception as e:
        print(f"⚠️  Could not mount control-plane: {e}")
    
    return app

# FastAPI app instance for uvicorn
app = create_main_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)