# Contributing to AI Sakhi

Thank you for your interest in contributing to AI Sakhi - Voice-First Health Companion! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/SakhiSathi.git
   cd SakhiSathi
   ```
3. **Set up the development environment**:
   ```bash
   python -m venv ai-sakhi-env
   ai-sakhi-env\Scripts\activate  # Windows
   # or
   source ai-sakhi-env/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
# or
git checkout -b docs/documentation-update
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `test/` - Test additions or modifications
- `refactor/` - Code refactoring

### 2. Make Your Changes

- Write clean, readable code following PEP 8 guidelines
- Add type hints to function parameters and return values
- Write docstrings for all classes and functions
- Keep functions focused and under 50 lines when possible
- Add comments for complex logic

### 3. Test Your Changes

Run the test suite before committing:
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_content_safety.py -v

# Run with coverage
pytest tests/ --cov=core --cov=modules --cov-report=html
```

### 4. Commit Your Changes

Write clear, descriptive commit messages:
```bash
git add .
git commit -m "Add feature: brief description

- Detailed point 1
- Detailed point 2
- Fixes #issue-number (if applicable)"
```

Commit message guidelines:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line should be 50 characters or less
- Reference issues and pull requests when relevant

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill in the PR template with:
   - Description of changes
   - Related issues
   - Testing performed
   - Screenshots (if UI changes)

## Code Style Guidelines

### Python Code Style

Follow PEP 8 with these specifics:
- **Indentation**: 4 spaces (no tabs)
- **Line length**: Maximum 100 characters
- **Imports**: Group in order: standard library, third-party, local
- **Naming**:
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_CASE`
  - Private methods: `_leading_underscore`

Example:
```python
from typing import Dict, List, Optional
import logging

from core.session_manager import SessionManager


class HealthModule:
    """Base class for health education modules."""
    
    def __init__(self, content_manager: ContentManager):
        """Initialize the health module."""
        self.content_manager = content_manager
        self.logger = logging.getLogger(__name__)
    
    def process_query(self, query: str, language_code: str) -> str:
        """
        Process user query and return response.
        
        Args:
            query: User's question or request
            language_code: Language code (e.g., 'hi', 'en')
            
        Returns:
            str: Response text in requested language
        """
        # Implementation here
        pass
```

### JavaScript Code Style

- Use ES6+ features
- Use `const` and `let`, avoid `var`
- Use arrow functions for callbacks
- Use template literals for string interpolation
- Add JSDoc comments for functions

### CSS Code Style

- Use meaningful class names
- Follow BEM naming convention when appropriate
- Group related properties together
- Use CSS variables for colors and common values

## Testing Guidelines

### Writing Tests

1. **Unit Tests**: Test individual functions and classes
   ```python
   def test_session_creation():
       """Test that sessions are created correctly."""
       manager = SessionManager()
       session = manager.create_session('en')
       assert session.language_preference == 'en'
       assert session.session_id is not None
   ```

2. **Integration Tests**: Test component interactions
   ```python
   def test_voice_processing_pipeline():
       """Test complete voice processing workflow."""
       # Setup components
       # Process voice input
       # Verify output
   ```

3. **Property-Based Tests**: Use Hypothesis for property testing
   ```python
   from hypothesis import given
   from hypothesis import strategies as st
   
   @given(st.text(min_size=1))
   def test_content_safety_handles_any_text(text):
       """Content safety validator should handle any text input."""
       validator = ContentSafetyValidator()
       result = validator.validate_user_query(text, 'en')
       assert result is not None
   ```

### Test Coverage

- Aim for at least 80% code coverage
- All new features must include tests
- Bug fixes should include regression tests

## Documentation

### Code Documentation

- All modules should have module-level docstrings
- All classes should have class-level docstrings
- All public functions should have docstrings with:
  - Brief description
  - Args section
  - Returns section
  - Raises section (if applicable)
  - Example usage (for complex functions)

### User Documentation

- Update README.md for user-facing changes
- Update QUICKSTART.md for setup/installation changes
- Add inline comments for complex logic
- Update API documentation for endpoint changes

## Pull Request Process

1. **Ensure all tests pass** locally before submitting
2. **Update documentation** as needed
3. **Add yourself to CONTRIBUTORS.md** (if first contribution)
4. **Request review** from maintainers
5. **Address review feedback** promptly
6. **Squash commits** if requested before merge

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts with main branch
- [ ] PR description clearly explains changes

## Reporting Issues

### Bug Reports

Include:
- Clear, descriptive title
- Steps to reproduce
- Expected behavior
- Actual behavior
- System information (OS, Python version)
- Error messages and stack traces
- Screenshots (if applicable)

### Feature Requests

Include:
- Clear, descriptive title
- Problem statement (what need does this address?)
- Proposed solution
- Alternative solutions considered
- Additional context

## Code Review Process

### For Contributors

- Be open to feedback
- Respond to comments promptly
- Ask questions if feedback is unclear
- Make requested changes or explain why not

### For Reviewers

- Be respectful and constructive
- Focus on code, not the person
- Explain the "why" behind suggestions
- Approve when ready, request changes if needed

## Community Guidelines

- Be respectful and inclusive
- Welcome newcomers
- Help others learn
- Focus on the mission: helping women and girls in rural areas
- Maintain cultural sensitivity in all contributions

## Questions?

If you have questions about contributing:
1. Check existing documentation
2. Search closed issues
3. Open a new issue with the "question" label
4. Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to AI Sakhi! Your work helps provide accessible health education to women and girls in rural India.
