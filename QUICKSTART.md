# AI Sakhi - Quick Start Guide

## Overview
This guide will help you get the AI Sakhi Voice-First Health Companion application up and running quickly.

## Prerequisites

### Required
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Optional (for production)
- AWS Account with S3, Transcribe, and Polly access
- Redis (for production caching)
- PostgreSQL/MySQL (for session persistence)

## Installation

### 1. Clone or Navigate to Project Directory
```bash
cd /path/to/ai-sakhi
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv ai-sakhi-env
ai-sakhi-env\Scripts\activate

# Linux/Mac
python3 -m venv ai-sakhi-env
source ai-sakhi-env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

### Development Mode (Mock Services)
The application runs in mock mode by default, which doesn't require AWS credentials.

```bash
python app_integrated.py
```

The application will start on `http://localhost:8080`

### Access the Application
Open your browser and navigate to:
- **Main Page**: http://localhost:8080
- **Health Check**: http://localhost:8080/health
- **Modules**: http://localhost:8080/modules

## Testing the Features

### 1. Health Check
```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Sakhi",
  "version": "1.0.0",
  "components": {
    "session_manager": {"status": "healthy"},
    "content_manager": {"status": "healthy"},
    "voice_interface": {"status": "healthy"},
    ...
  }
}
```

### 2. Text Input (Fallback Mode)
```bash
curl -X POST http://localhost:8080/api/text/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Tell me about puberty"}'
```

### 3. Emergency Contacts (Offline)
```bash
curl http://localhost:8080/api/emergency
```

### 4. Change Language
```bash
curl -X POST http://localhost:8080/language/en
```

### 5. Get Statistics
```bash
curl http://localhost:8080/api/stats
```

## Running Tests

### Run All Tests
```bash
# Set PYTHONPATH
$env:PYTHONPATH="."  # Windows PowerShell
export PYTHONPATH="."  # Linux/Mac

# Run specific test suites
python tests/test_content_safety.py
python tests/test_reminder_system.py
python tests/test_session_manager.py
python tests/test_content_manager.py
```

### Expected Output
```
🧪 Running AI Sakhi Content Safety Tests...
...
✅ All content safety tests passed!
```

## Configuration

### Environment Variables (Optional)

Create a `.env` file in the project root:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
PORT=8080
DEBUG=True

# AWS Configuration (for production)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=ai-sakhi-content

# Session Configuration
SESSION_TIMEOUT_MINUTES=30
ENABLE_SESSION_PERSISTENCE=False

# Content Configuration
CONTENT_CACHE_SIZE=1000
CONTENT_CACHE_TTL=3600
```

## Switching to Production Mode

### 1. Configure AWS Services

#### S3 Bucket Setup
```bash
# Create S3 bucket
aws s3 mb s3://ai-sakhi-content --region us-east-1

# Upload content
aws s3 sync ./content s3://ai-sakhi-content/
```

#### IAM Permissions
Ensure your AWS user/role has:
- S3: GetObject, ListBucket
- Transcribe: StartTranscriptionJob, GetTranscriptionJob
- Polly: SynthesizeSpeech

### 2. Update Application Configuration

Edit `app_integrated.py`:

```python
# Change from mock mode to production
content_manager = ContentManager(
    s3_bucket_name='ai-sakhi-content',
    aws_region='us-east-1',
    use_mock=False  # Change to False
)

speech_processor = SpeechProcessor(
    aws_region='us-east-1',
    use_mock=False  # Change to False
)

voice_interface = VoiceInterface(
    speech_processor=speech_processor,
    content_manager=content_manager,
    session_manager=session_manager,
    use_mock=False  # Change to False
)
```

### 3. Run with Production Settings
```bash
export SECRET_KEY="your-production-secret-key"
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"

python app_integrated.py
```

## Troubleshooting

### Issue: Port Already in Use
```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8080
kill -9 <PID>
```

### Issue: Module Import Errors
```bash
# Ensure PYTHONPATH is set
$env:PYTHONPATH="."  # Windows PowerShell
export PYTHONPATH="."  # Linux/Mac

# Or install in development mode
pip install -e .
```

### Issue: AWS Credentials Not Found
```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

### Issue: Tests Failing
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Run tests with verbose output
python -m pytest tests/ -v
```

## Common Tasks

### View Logs
Logs are printed to console by default. To save to file:
```bash
python app_integrated.py > app.log 2>&1
```

### Clear Cache
The application uses in-memory caching. Restart the application to clear cache:
```bash
# Stop the application (Ctrl+C)
# Start again
python app_integrated.py
```

### Reset Sessions
Sessions are stored in memory. Restart the application to reset all sessions.

### Update Content
In mock mode, content is defined in `core/content_manager.py`. In production mode, upload new content to S3:
```bash
aws s3 sync ./content s3://ai-sakhi-content/
```

## API Examples

### Create Prenatal Reminder
```bash
curl -X POST http://localhost:8080/api/reminders \
  -H "Content-Type: application/json" \
  -d '{
    "type": "prenatal_appointment",
    "appointment_date": "2026-02-15T10:00:00",
    "doctor_name": "Dr. Sharma",
    "clinic_name": "City Health Center"
  }'
```

### Get User Reminders
```bash
curl http://localhost:8080/api/reminders
```

### Process Text Query
```bash
curl -X POST http://localhost:8080/api/text/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "मुझे गर्भावस्था के बारे में बताएं"
  }'
```

## Development Tips

### Hot Reload
Flask's debug mode enables hot reload:
```python
app.run(debug=True)  # Already enabled in app_integrated.py
```

### Testing Individual Components
```python
# Test session manager
from core.session_manager import SessionManager
sm = SessionManager()
session = sm.create_session('hi')
print(session.to_json())

# Test content manager
from core.content_manager import ContentManager
cm = ContentManager('bucket', use_mock=True)
content = cm.get_module_content('puberty', 'hi')
print(len(content))

# Test content safety
from core.content_safety import ContentSafetyValidator
validator = ContentSafetyValidator()
result = validator.validate_content("Learn about health")
print(result.is_safe)
```

### Adding New Health Module
1. Create module class inheriting from `BaseHealthModule`
2. Implement required abstract methods
3. Add to `health_modules` dict in `app_integrated.py`
4. Create content in `ContentManager._initialize_mock_content()`

## Production Deployment

### Using Gunicorn (Recommended)
```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:8080 app_integrated:app
```

### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app_integrated:app"]
```

Build and run:
```bash
docker build -t ai-sakhi .
docker run -p 8080:8080 ai-sakhi
```

### Using Nginx (Reverse Proxy)
```nginx
server {
    listen 80;
    server_name ai-sakhi.example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Support

### Documentation
- `integration-summary.md` - Complete integration overview
- `final-status-report.md` - Status and deployment checklist
- `.kiro/specs/sakhi-saathi-ai/design.md` - System design
- `.kiro/specs/sakhi-saathi-ai/requirements.md` - Requirements

### Logs
Check application logs for errors:
```bash
# View recent logs
tail -f app.log

# Search for errors
grep ERROR app.log
```

### Health Check
Monitor system health:
```bash
curl http://localhost:8080/health | python -m json.tool
```

## Next Steps

1. ✅ Run the application in development mode
2. ✅ Test all API endpoints
3. ✅ Run test suites
4. ⏳ Configure AWS services for production
5. ⏳ Deploy to production environment
6. ⏳ Set up monitoring and alerting
7. ⏳ Conduct user acceptance testing

---

**Quick Start Version**: 1.0
**Last Updated**: 2026-02-06
**Status**: Ready for Development
