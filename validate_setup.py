#!/usr/bin/env python3
"""
Setup validation script to ensure all components are properly integrated.
"""

import sys
import importlib
from pathlib import Path


def validate_imports():
    """Validate that all modules can be imported successfully."""
    print("🔍 Validating imports...")
    
    modules_to_test = [
        # Core application
        'app.main',
        'app.config.settings',
        'app.config.database',
        'app.config.database_init',
        'app.config.validation',
        
        # Models
        'app.models.requests',
        'app.models.responses',
        'app.models.database',
        'app.models.validation',
        
        # Services
        'app.services.ai_service',
        'app.services.mock_ai_service',
        'app.services.text_service',
        
        # Controllers
        'app.controllers.text_controller',
        
        # Routes
        'app.routes.api',
        'app.routes.text_routes',
        
        # Middlewares
        'app.middlewares.logging',
        'app.middlewares.error_handler',
        'app.middlewares.cors',
        
        # Background service
        'app.background.listener',
        'app.background.client',
        
        # Utils
        'app.utils.helpers',
        'app.utils.logging_utils',
        'app.utils.constants',
        'app.utils.validation_utils',
    ]
    
    failed_imports = []
    
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {module_name}")
        except ImportError as e:
            print(f"  ❌ {module_name}: {str(e)}")
            failed_imports.append((module_name, str(e)))
    
    if failed_imports:
        print(f"\n❌ {len(failed_imports)} import failures:")
        for module, error in failed_imports:
            print(f"  - {module}: {error}")
        return False
    
    print(f"✅ All {len(modules_to_test)} modules imported successfully")
    return True


def validate_file_structure():
    """Validate that all required files exist."""
    print("\n📁 Validating file structure...")
    
    required_files = [
        # Core files
        'app/__init__.py',
        'app/main.py',
        'run.py',
        'requirements.txt',
        'README.md',
        '.env.example',
        
        # Configuration
        'app/config/__init__.py',
        'app/config/settings.py',
        'app/config/database.py',
        'app/config/database_init.py',
        'app/config/validation.py',
        
        # Models
        'app/models/__init__.py',
        'app/models/requests.py',
        'app/models/responses.py',
        'app/models/database.py',
        'app/models/validation.py',
        
        # Services
        'app/services/__init__.py',
        'app/services/ai_service.py',
        'app/services/mock_ai_service.py',
        'app/services/text_service.py',
        
        # Controllers
        'app/controllers/__init__.py',
        'app/controllers/text_controller.py',
        
        # Routes
        'app/routes/__init__.py',
        'app/routes/api.py',
        'app/routes/text_routes.py',
        
        # Middlewares
        'app/middlewares/__init__.py',
        'app/middlewares/logging.py',
        'app/middlewares/error_handler.py',
        'app/middlewares/cors.py',
        
        # Background service
        'app/background/__init__.py',
        'app/background/listener.py',
        'app/background/client.py',
        
        # Utils
        'app/utils/__init__.py',
        'app/utils/helpers.py',
        'app/utils/logging_utils.py',
        'app/utils/constants.py',
        'app/utils/validation_utils.py',
        
        # Tests
        'tests/__init__.py',
        'tests/conftest.py',
        'tests/test_services.py',
        'tests/test_controllers.py',
        'tests/test_utils.py',
        'tests/test_api.py',
        'tests/test_integration.py',
        
        # Docker and deployment
        'Dockerfile',
        'docker-compose.yml',
        '.gitignore',
        'pytest.ini',
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"  ❌ {file_path}")
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ {len(missing_files)} missing files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print(f"✅ All {len(required_files)} required files exist")
    return True


def validate_configuration():
    """Validate configuration setup."""
    print("\n⚙️  Validating configuration...")
    
    try:
        from app.config.settings import settings
        from app.config.validation import validate_configuration
        
        # Check that settings can be loaded
        print(f"  ✅ Settings loaded: {settings.app_name} v{settings.app_version}")
        
        # Check validation functions
        is_valid, errors = validate_configuration()
        if errors:
            print(f"  ⚠️  Configuration has {len(errors)} potential issues:")
            for error in errors[:3]:  # Show first 3 errors
                print(f"    - {error}")
            if len(errors) > 3:
                print(f"    ... and {len(errors) - 3} more")
        else:
            print("  ✅ Configuration validation passed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration validation failed: {str(e)}")
        return False


def validate_models():
    """Validate that models can be instantiated."""
    print("\n📋 Validating models...")
    
    try:
        from app.models.requests import TextModificationRequest, TextOperation
        from app.models.responses import TextModificationResponse
        from datetime import datetime
        
        # Test request model
        request = TextModificationRequest(
            text="Test text",
            operation=TextOperation.IMPROVE,
            user_id="test_user"
        )
        print("  ✅ TextModificationRequest model")
        
        # Test response model
        response = TextModificationResponse(
            original_text="Test text",
            modified_text="Improved text",
            operation=TextOperation.IMPROVE,
            timestamp=datetime.utcnow(),
            processing_time=1.0,
            word_count_original=2,
            word_count_modified=2
        )
        print("  ✅ TextModificationResponse model")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model validation failed: {str(e)}")
        return False


def validate_services():
    """Validate that services can be instantiated."""
    print("\n🔧 Validating services...")
    
    try:
        from app.services.text_service import TextService
        from app.services.mock_ai_service import MockAIService
        
        # Test text service
        text_service = TextService()
        print("  ✅ TextService instantiated")
        
        # Test mock AI service
        mock_ai_service = MockAIService()
        print("  ✅ MockAIService instantiated")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Service validation failed: {str(e)}")
        return False


def validate_fastapi_app():
    """Validate that FastAPI app can be created."""
    print("\n🚀 Validating FastAPI application...")
    
    try:
        from app.main import app
        
        # Check that app is a FastAPI instance
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)
        print("  ✅ FastAPI app created")
        
        # Check that routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = [
            "/",
            "/ping",
            "/api/v1/text/modify",
            "/api/v1/text/operations",
            "/api/v1/health"
        ]
        
        for route in expected_routes:
            if route in routes:
                print(f"  ✅ Route registered: {route}")
            else:
                print(f"  ❌ Route missing: {route}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ FastAPI app validation failed: {str(e)}")
        return False


def main():
    """Run all validations."""
    print("🤖 AI Text Assistant Backend - Setup Validation")
    print("=" * 50)
    
    validations = [
        ("File Structure", validate_file_structure),
        ("Imports", validate_imports),
        ("Configuration", validate_configuration),
        ("Models", validate_models),
        ("Services", validate_services),
        ("FastAPI App", validate_fastapi_app),
    ]
    
    results = []
    
    for name, validation_func in validations:
        try:
            result = validation_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} validation crashed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Validation Summary:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {name}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{len(results)} validations passed")
    
    if passed == len(results):
        print("\n🎉 All validations passed! The application is ready to run.")
        print("\nNext steps:")
        print("  1. Copy .env.example to .env and configure it")
        print("  2. Run: python run.py setup")
        print("  3. Run: python run.py server")
        return True
    else:
        print(f"\n⚠️  {len(results) - passed} validation(s) failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)