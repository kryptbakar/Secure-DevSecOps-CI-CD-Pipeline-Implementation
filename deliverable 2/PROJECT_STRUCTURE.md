# 📁 Project Structure Guide

A clean, organized DevSecOps CI/CD Pipeline implementation with Shift Left Security.

```
CdPipeline/
│
├── 📂 app/                          # Flask Application (Core Project)
│   ├── __init__.py                  # Package initialization
│   ├── main.py                      # Flask app factory & setup
│   ├── config.py                    # Configuration management
│   ├── auth.py                      # Authentication logic
│   ├── db.py                        # Database initialization
│   ├── security.py                  # Security headers & protections
│   ├── rbac.py                      # Role-Based Access Control
│   ├── audit.py                     # Audit logging
│   ├── api_keys.py                  # API key management
│   ├── items.py                     # Items endpoints
│   ├── validators.py                # Input validation rules
│   └── templates/                   # HTML templates
│       ├── index.html
│       └── dashboard.html
│
├── 📂 tests/                        # Unit & Integration Tests
│   ├── conftest.py                  # Pytest configuration
│   ├── test_app.py                  # Application tests
│   └── test_security.py             # Security tests
│
├── 📂 docs/                         # Documentation & Reports
│   ├── D1_Risk_Management.pdf
│   ├── D1_Security_Requirements_Planning.pdf
│   ├── D1_Threat_Modeling.pdf
│   ├── project proposal.pdf
│   └── workflow Documentation.pdf
│
├── 📂 .github/                      # GitHub Actions & CI/CD
│   └── workflows/                   # GitHub action workflows
│
├── 📂 .venv/                        # Virtual Environment (auto-created)
│
├── 🔧 Configuration Files
│   ├── .gitignore                   # Git ignore rules
│   ├── .pre-commit-config.yaml      # Pre-commit hooks config
│   └── requirements.txt             # Python dependencies
│
├── 🐍 Python entry points
│   ├── run.py                       # Dev server entry point
│   └── remediate.py                 # Auto-update vulnerable dependencies
│
└── 📋 Documentation
    ├── README.md                    # Project overview & setup
    └── PROJECT_STRUCTURE.md         # This file
```

## 📊 Key Components

### `app/` - Core Flask Application
- **main.py**: Initializes Flask app with security config
- **config.py**: Centralized configuration (secret key, session settings, etc.)
- **auth.py**: Authentication middleware & logic
- **security.py**: Security headers, CORS, XSS protection
- **rbac.py**: Role-Based Access Control implementation
- **db.py**: Database connection & initialization
- **audit.py**: Audit trail logging
- **validators.py**: Input validation & sanitization
- **api_keys.py**: API key management endpoints
- **items.py**: Application business logic endpoints

### `tests/` - Test Suite
- Pytest-based testing
- Unit tests for business logic
- Security validation tests
- Integration tests

### `docs/` - Documentation
- Risk management assessments
- Security requirements planning
- Threat modeling documents
- Workflow documentation

### `.github/` - CI/CD Pipelines
- GitHub Actions workflows
- Automated security scanning (SAST, SCA)
- Deployment automation

## 🚀 Quick Start

```bash
# Create & activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
python run.py
```

## 🔒 Security Scanning

```bash
# Static Application Security Testing (SAST)
bandit -r app/

# Software Composition Analysis (SCA) - Dependency scanning
pip-audit

# Auto-remediate vulnerable dependencies
python remediate.py
```

## ✅ Running Tests

```bash
pytest tests/
```

## 📝 Notes

- **Virtual Environment**: Located in `.venv/` (created locally, excluded from Git)
- **Database**: `app.db` is auto-generated and excluded from Git
- **Removed**: VS Code extensions, cache files, and duplicate environments have been cleaned up
- **Organization**: Follows Flask best practices with clear separation of concerns
