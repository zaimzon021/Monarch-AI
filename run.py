#!/usr/bin/env python3
"""
Application startup script for AI Text Assistant Backend.
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import settings
from app.config.validation import validate_configuration
from app.config.database_init import initialize_database, create_indexes
import structlog

logger = structlog.get_logger(__name__)


def setup_environment():
    """Setup environment and validate configuration."""
    print("🔧 Setting up environment...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Please copy .env.example to .env and configure it.")
        print("   cp .env.example .env")
        return False
    
    # Validate configuration
    is_valid, errors = validate_configuration()
    if not is_valid:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print("✅ Configuration validated successfully")
    return True


async def setup_database():
    """Setup database connection and indexes."""
    print("🗄️  Setting up database...")
    
    try:
        # Initialize database
        success = await initialize_database()
        if not success:
            print("❌ Failed to initialize database")
            return False
        
        # Create indexes
        await create_indexes()
        print("✅ Database setup completed")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        return False


def run_server():
    """Run the FastAPI server."""
    import uvicorn
    
    print(f"🚀 Starting AI Text Assistant Backend on {settings.host}:{settings.port}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"🔍 Health Check: http://{settings.host}:{settings.port}/api/v1/health")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )


def run_background_service():
    """Run the background service."""
    from app.background.listener import run_standalone
    
    print(f"🔧 Starting background service on port {settings.background_service_port}")
    asyncio.run(run_standalone())


def run_tests():
    """Run the test suite."""
    import subprocess
    
    print("🧪 Running test suite...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short"
        ], check=True)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Some tests failed")
        return False


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Text Assistant Backend")
    parser.add_argument(
        "command", 
        choices=["server", "background", "test", "setup"],
        help="Command to run"
    )
    parser.add_argument(
        "--skip-setup", 
        action="store_true",
        help="Skip environment and database setup"
    )
    
    args = parser.parse_args()
    
    print("🤖 AI Text Assistant Backend")
    print("=" * 40)
    
    # Setup environment (unless skipped)
    if not args.skip_setup:
        if not setup_environment():
            sys.exit(1)
        
        if args.command in ["server", "background"]:
            if not await setup_database():
                sys.exit(1)
    
    # Run the requested command
    if args.command == "server":
        run_server()
    elif args.command == "background":
        run_background_service()
    elif args.command == "test":
        success = run_tests()
        sys.exit(0 if success else 1)
    elif args.command == "setup":
        print("✅ Setup completed successfully")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())