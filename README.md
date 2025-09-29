# AI Text Assistant Backend

A comprehensive FastAPI-based backend service for AI-powered text modification with Windows background service capabilities. This service provides REST API endpoints for text processing operations like summarization, improvement, translation, and analysis, along with a Windows background service for system-wide text modification.

## Features

- 🤖 **AI-Powered Text Processing**: Support for multiple text operations (summarize, improve, translate, correct, expand, simplify, analyze)
- 🔄 **Background Service**: Windows service for system-wide text modification
- 📊 **User Analytics**: Track user modifications and provide statistics
- 🗄️ **MongoDB Integration**: Persistent storage for modification history
- 🔍 **Health Monitoring**: Comprehensive health checks and monitoring
- 📝 **Request Logging**: Detailed logging with correlation IDs
- 🛡️ **Error Handling**: Robust error handling and validation
- 📚 **API Documentation**: Auto-generated OpenAPI documentation
- 🧪 **Comprehensive Testing**: Full test suite with mocking

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
app/
├── config/          # Configuration and settings
│   ├── settings.py      # Pydantic settings with environment variables
│   ├── database.py      # MongoDB connection management
│   ├── database_init.py # Database lifecycle and initialization
│   └── validation.py    # Configuration validation
├── models/          # Data models and validation
│   ├── requests.py      # Request models and enums
│   ├── responses.py     # Response models
│   ├── database.py      # Database models for MongoDB
│   └── validation.py    # Request validation utilities
├── services/        # Business logic layer
│   ├── ai_service.py    # AI service integration
│   ├── mock_ai_service.py # Mock AI service for testing
│   └── text_service.py  # Text processing business logic
├── controllers/     # Request handling layer
│   └── text_controller.py # Text modification controllers
├── routes/          # API route definitions
│   ├── api.py          # Main API router
│   └── text_routes.py  # Text processing routes
├── middlewares/     # Custom middleware
│   ├── logging.py      # Request/response logging with correlation IDs
│   ├── error_handler.py # Global error handling
│   └── cors.py         # CORS configuration
├── background/      # Windows background service
│   ├── listener.py     # Background service listener
│   └── client.py       # Background service client
└── utils/           # Utility functions
    ├── helpers.py      # General helper functions
    ├── logging_utils.py # Logging configuration
    ├── constants.py    # Application constants
    └── validation_utils.py # Validation utilities
```

## Quick Start

### Using the Startup Script (Recommended)

1. **Setup Environment**:
   ```bash
   python run.py setup
   ```

2. **Run the Server**:
   ```bash
   python run.py server
   ```

3. **Run Background Service** (optional):
   ```bash
   python run.py background
   ```

4. **Run Tests**:
   ```bash
   python run.py test
   ```

### Manual Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Configuration

### Required Environment Variables

```bash
# Database (Required)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=ai_text_assistant

# AI Service (Required)
AI_API_KEY=your_ai_api_key_here
AI_API_ENDPOINT=https://api.openai.com/v1
AI_MODEL=gpt-3.5-turbo
```

### Optional Environment Variables

```bash
# Application
APP_NAME="AI Text Assistant Backend"
DEBUG=false
HOST=127.0.0.1
PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Background Service
BACKGROUND_SERVICE_PORT=8001
BACKGROUND_SERVICE_ENABLED=true

# Security
SECRET_KEY=your_secret_key_here
CORS_ORIGINS=["*"]
```

See `.env.example` for complete configuration options.

## API Endpoints

### Text Processing

- `POST /api/v1/text/modify` - Modify text using AI
- `POST /api/v1/text/analyze` - Analyze text content
- `GET /api/v1/text/operations` - Get supported operations

### User Data

- `GET /api/v1/text/history/{user_id}` - Get modification history
- `GET /api/v1/text/statistics/{user_id}` - Get user statistics

### System

- `GET /api/v1/health` - Health check
- `GET /api/v1/status` - Service status
- `GET /docs` - API documentation

## Supported Text Operations

| Operation | Description |
|-----------|-------------|
| `summarize` | Create a concise summary of the text |
| `improve` | Improve text clarity, grammar, and readability |
| `translate` | Translate text to another language |
| `correct` | Correct grammar, spelling, and punctuation |
| `expand` | Expand and elaborate with more details |
| `simplify` | Simplify text for easier understanding |
| `analyze` | Analyze text and provide insights |

## Background Service

The Windows background service allows system-wide text modification:

### Installation

```bash
# Install as Windows service
python app/background/listener.py install

# Start the service
python app/background/listener.py start
```

### Usage

```python
from app.background.client import BackgroundServiceClient

client = BackgroundServiceClient()
response = await client.send_text_request(
    text="Text to improve",
    operation=TextOperation.IMPROVE,
    source_application="notepad.exe"
)
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python run.py test

# Run specific test files
pytest tests/test_services.py -v
pytest tests/test_controllers.py -v
pytest tests/test_utils.py -v
pytest tests/test_api.py -v
```

## Monitoring and Logging

### Health Checks

- **Application Health**: `GET /api/v1/health`
- **Database Health**: Included in health check response
- **AI Service Health**: Included in health check response

### Logging

The application uses structured logging with correlation IDs:

```json
{
  "timestamp": "2023-12-01T10:00:00Z",
  "level": "INFO",
  "correlation_id": "abc-123-def",
  "message": "Request completed",
  "method": "POST",
  "url": "/api/v1/text/modify",
  "status_code": 200,
  "process_time": 1.23
}
```

## Error Handling

The application provides consistent error responses:

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "timestamp": "2023-12-01T10:00:00Z",
  "request_id": "abc-123-def",
  "error_type": "validation_error",
  "is_retryable": false
}
```

## Development

### Project Structure

The codebase follows clean architecture principles:

- **Controllers**: Handle HTTP requests and responses
- **Services**: Contain business logic
- **Models**: Define data structures and validation
- **Middlewares**: Handle cross-cutting concerns
- **Utils**: Provide helper functions

### Adding New Operations

1. Add operation to `TextOperation` enum in `models/requests.py`
2. Update AI service to handle the new operation
3. Add operation description in `controllers/text_controller.py`
4. Write tests for the new operation

### Database Schema

The application uses MongoDB with the following collections:

- `modification_records`: Store text modification history
- `user_sessions`: Track user sessions
- `system_metrics`: Store performance metrics

## Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "run.py", "server", "--skip-setup"]
```

### Production Considerations

- Set `DEBUG=false` in production
- Use a production WSGI server like Gunicorn
- Configure proper CORS origins
- Set up log aggregation
- Monitor health endpoints
- Use environment-specific configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.