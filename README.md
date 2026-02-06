# AI Sakhi - Voice-First Health Companion

A trusted health companion for women and girls in rural areas, providing voice-first health education, safety awareness, and guidance in multiple Indian languages.

![AI Sakhi Logo](ai-sakhi-logo.svg)

## Overview

AI Sakhi is a Flask-based web application designed to provide accessible health education to women and girls in rural India. The application features:

- **Voice-First Interface**: Natural language processing with AWS Transcribe and Polly
- **Multi-Language Support**: Hindi, English, Bengali, Tamil, Telugu, and Marathi
- **5 Health Education Modules**: Puberty, Safety & Mental Support, Menstrual Health, Pregnancy Guidance, and Government Resources
- **Medical Boundary Compliance**: Content safety validation to ensure educational (not diagnostic) information
- **Offline Emergency Access**: Critical emergency contacts available even without internet

## Features

### Core Components
- **Session Management**: Secure user session handling with 30-minute timeout
- **Content Management**: AWS S3 integration for multimedia content delivery
- **Speech Processing**: Voice input/output with fallback mechanisms
- **Reminder System**: Prenatal appointment reminders and notifications
- **Error Handling**: Graceful degradation with comprehensive error recovery

### Health Modules
1. **Puberty Education**: Body changes, menstruation, and hygiene
2. **Safety & Mental Support**: Good/bad touch awareness and emotional support
3. **Menstrual Shopping Guide**: Product comparison and selection guidance
4. **Pregnancy Guidance**: Nutrition tips and danger sign education
5. **Government Resources**: Health schemes and programs information

## Technology Stack

- **Backend**: Python 3.12, Flask 3.1.2
- **AWS Services**: S3, Transcribe, Polly (with mock mode for development)
- **Testing**: pytest, Hypothesis (property-based testing)
- **Internationalization**: Flask-Babel
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)

## Installation

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd SakhiSathi
```

2. Create and activate virtual environment:
```bash
python -m venv ai-sakhi-env
# On Windows:
ai-sakhi-env\Scripts\activate
# On Linux/Mac:
source ai-sakhi-env/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app_integrated.py
```

The application will start on `http://localhost:8080`

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup and testing instructions.

## Project Structure

```
SakhiSathi/
├── core/                      # Core system components
│   ├── session_manager.py     # User session management
│   ├── content_manager.py     # Content delivery system
│   ├── speech_processor.py    # Voice processing
│   ├── voice_interface.py     # Voice interaction handling
│   ├── reminder_system.py     # Appointment reminders
│   ├── content_safety.py      # Medical boundary compliance
│   └── error_handler.py       # Error handling & recovery
├── modules/                   # Health education modules
│   ├── base_health_module.py
│   ├── puberty_education_module.py
│   ├── safety_mental_support_module.py
│   ├── menstrual_guide_module.py
│   ├── pregnancy_guidance_module.py
│   └── government_resources_module.py
├── models/                    # Data models
│   └── data_models.py
├── templates/                 # HTML templates
├── static/                    # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
├── tests/                     # Unit and integration tests
├── .kiro/                     # Kiro spec files
│   └── specs/sakhi-saathi-ai/
├── app_integrated.py          # Main Flask application
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test suites:
```bash
# Session management tests
pytest tests/test_session_manager.py -v

# Content safety tests
pytest tests/test_content_safety.py -v

# Speech processor tests
pytest tests/test_speech_processor.py -v
```

## Configuration

### Environment Variables
Create a `.env` file (not committed to git) with:
```
SECRET_KEY=your-secret-key-here
AWS_REGION=us-east-1
S3_BUCKET_NAME=ai-sakhi-content
```

### Mock Mode
The application runs in mock mode by default (no AWS credentials required). To use real AWS services, set `use_mock=False` in `app_integrated.py` and configure AWS credentials.

## API Endpoints

- `GET /` - Main landing page
- `GET /health` - Health check endpoint
- `GET /modules` - List all health modules
- `GET /module/<module_name>` - Module detail page
- `POST /api/voice/process` - Process voice input
- `POST /api/text/process` - Process text input (fallback)
- `GET /api/emergency` - Get emergency contacts
- `GET/POST /api/reminders` - Manage reminders
- `POST /language/<code>` - Change language
- `GET /api/stats` - Get system statistics

## Development

### Running in Development Mode
```bash
python app_integrated.py
```
The application runs with Flask's debug mode enabled on port 8080.

### Code Style
- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for all classes and functions
- Keep functions focused and under 50 lines when possible

## Documentation

- [Requirements](. kiro/specs/sakhi-saathi-ai/requirements.md)
- [Design Document](.kiro/specs/sakhi-saathi-ai/design.md)
- [Implementation Tasks](.kiro/specs/sakhi-saathi-ai/tasks.md)
- [Integration Summary](integration-summary.md)
- [Final Status Report](final-status-report.md)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is developed for educational and social impact purposes.

## Acknowledgments

- Designed for women and girls in rural India
- Built with accessibility and cultural sensitivity in mind
- Supports multiple Indian languages for broader reach
- Focuses on health education, not medical diagnosis

## Contact

For questions or support, please open an issue in the repository.

---

**Note**: This application provides educational health information only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified health providers with questions about medical conditions.
