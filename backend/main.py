#!/usr/bin/env python3
"""
Main entry point for the data onboarding platform
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment configuration
from dotenv import load_dotenv
load_dotenv(project_root / "config" / ".env")

# Import from organized structure
from observability import get_control_plane_app

def main():
    """Main application entry point"""
    print("🚀 Starting Data Onboarding Platform")
    print("📁 Organized backend structure:")
    print("   📊 observability/ - Control-plane agents and workflows")
    print("   🗄️  core/ - Database and models")
    print("   🌐 api/ - FastAPI routes and middleware")
    print("   ⚙️  config/ - Configuration files")
    print("   🧪 tests/ - Test suites by category")
    
    # Get the control-plane app
    app = get_control_plane_app()
    return app

# FastAPI app instance for uvicorn
app = main()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)