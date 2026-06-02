# Contributing to Secure Enterprise RAG

## Welcome! 👋

We're excited you want to contribute to our Secure Enterprise RAG Architecture! This document provides guidelines and instructions for contributing.

## Code of Conduct

We are committed to providing a welcoming and inspiring community. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git
- Node.js 18+ (for frontend work)

### Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/Secure-Enterprise-RAG.git
cd Secure-Enterprise-RAG

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start services
docker-compose up --build
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/description-of-feature
# or
git checkout -b fix/description-of-bug
```

### 2. Make Your Changes

- Write clean, readable code following PEP 8
- Add docstrings to functions
- Include type hints
- Write tests

### 3. Test Your Changes

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src

# Type checking
mypy .
```

### 4. Commit and Push

```bash
git commit -m "feat: add RBAC enforcement layer"
git push origin feature/your-feature
```

## Pull Request Guidelines

- Clear title describing changes
- Reference related issues
- Include test coverage
- Update documentation

## Code Style

- PEP 8 compliance
- Type hints required
- Docstrings for all functions
- Maximum line length: 100 characters

## Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Security tests
bandit -r . -ll
```

## Questions?

Open a discussion or contact vamshi@example.com

Thank you for contributing! 🙏
