# Contributing to SpotBot

Thank you for your interest in contributing to SpotBot! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Basic knowledge of Python (FastAPI) and JavaScript (React)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/spotbot.git
   cd spotbot
   ```

2. **Set Up Environment**
   ```bash
   cp .env.example .env
   ```

3. **Start Development Environment**
   ```bash
   docker-compose up --build
   ```

4. **Verify Setup**
   ```bash
   ./test.sh
   ```

## 📝 Development Workflow

### Making Changes

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Backend: Edit files in `backend/app/`
   - AI Detector: Edit files in `ai-detector/app/`
   - Frontend: Edit files in `frontend/src/`

3. **Test Changes**
   ```bash
   # Run test suite
   ./test.sh
   
   # Check specific service logs
   docker-compose logs -f backend
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

### Commit Message Format

Use conventional commits format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add video detection support
fix: correct confidence score calculation
docs: update API documentation
```

## 🏗️ Project Structure

### Backend (`backend/`)
```
app/
├── api/v1/
│   ├── endpoints/    # API route handlers
│   └── router.py     # Route configuration
├── core/             # Core functionality
│   ├── config.py     # Configuration
│   ├── database.py   # Database setup
│   ├── redis_client.py
│   └── security.py   # Auth utilities
├── models/           # SQLAlchemy models
└── schemas/          # Pydantic schemas
```

### AI Detector (`ai-detector/`)
```
app/
├── detectors/        # Detection algorithms
│   ├── text_detector.py
│   ├── image_detector.py
│   └── url_detector.py
├── main.py          # FastAPI app
└── schemas.py       # Request/response models
```

### Frontend (`frontend/`)
```
src/
├── api/             # API client
├── components/      # Reusable components
├── pages/           # Page components
├── store/           # State management
└── App.jsx         # Main app component
```

## 🧪 Testing

### Running Tests

```bash
# Full test suite
./test.sh

# Specific service tests
docker-compose exec backend pytest
```

### Adding Tests

- Backend: Add tests in `backend/tests/`
- Frontend: Add tests in `frontend/src/__tests__/`

## 📋 Areas for Contribution

### High Priority
- [ ] Improve AI detection accuracy
- [ ] Add file upload support
- [ ] Implement rate limiting
- [ ] Add more LLM model signatures
- [ ] Improve error handling

### Medium Priority
- [ ] Dashboard analytics implementation
- [ ] User profile pages
- [ ] Email verification
- [ ] Export detection results
- [ ] API key management

### Future Features (Phase 2)
- [ ] Crowdsourced bot reporting
- [ ] Bot network visualization
- [ ] Real-time detection alerts
- [ ] Browser extension
- [ ] Mobile app

## 🔧 Technical Guidelines

### Python (Backend/AI Detector)

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions
- Use async/await for I/O operations

```python
async def detect_content(
    content: str,
    content_type: str
) -> DetectionResult:
    """
    Detect if content is AI-generated.
    
    Args:
        content: The content to analyze
        content_type: Type of content (text, image, etc.)
        
    Returns:
        DetectionResult with confidence scores
    """
    pass
```

### JavaScript/React (Frontend)

- Use functional components with hooks
- Keep components small and focused
- Use proper prop types
- Follow consistent naming conventions

```javascript
export default function MyComponent({ prop1, prop2 }) {
  const [state, setState] = useState(null)
  
  // Component logic
  
  return (
    // JSX
  )
}
```

### Database

- Use migrations for schema changes
- Add indexes for frequently queried fields
- Use transactions for multi-step operations

### API Design

- Follow RESTful principles
- Use appropriate HTTP methods
- Return meaningful status codes
- Include error details in responses

## 🐛 Bug Reports

### Before Submitting

1. Check existing issues
2. Verify it's reproducible
3. Test with latest version

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Docker version: [e.g., 24.0.0]
- Browser: [e.g., Chrome 120]

**Additional context**
Logs, screenshots, etc.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Problem**
What problem does this solve?

**Proposed Solution**
How would you solve it?

**Alternatives**
What other solutions have you considered?

**Use Case**
Real-world scenario where this would be useful.
```

## 📖 Documentation

### Improving Documentation

- Update README.md for major changes
- Update QUICKSTART.md for setup changes
- Update ARCHITECTURE.md for design changes
- Add inline comments for complex logic
- Update API documentation in code

## 🎯 Code Review Process

1. **Submit PR** with clear description
2. **Automated Checks** must pass
3. **Code Review** by maintainers
4. **Address Feedback** if requested
5. **Merge** once approved

### PR Checklist

- [ ] Code follows project style
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts
- [ ] All tests passing

## 🤝 Community

### Getting Help

- GitHub Issues: Bug reports and feature requests
- Discussions: Questions and general discussion
- Discord (future): Real-time chat

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to SpotBot! 🎉
