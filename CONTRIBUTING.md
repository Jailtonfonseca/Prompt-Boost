# Contributing to Prompt-Boost

Thank you for your interest in contributing to Prompt-Boost!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Prompt-Boost.git`
3. Create a branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Code Style

### Python
- Follow PEP 8
- Use type hints where possible
- Max line length: 88 characters (Black formatter)
- Run `black .` before committing

### JavaScript/React
- Use functional components with hooks
- Follow React hooks rules
- Run ESLint: `npm run lint`

## Testing

### Backend
```bash
cd backend
pytest -v
```

### Frontend
```bash
cd frontend
npm test
```

## Commit Messages

Use clear, descriptive commit messages:
- `feat: add new prompt template feature`
- `fix: resolve CORS issue in production`
- `docs: update README with installation steps`
- `refactor: simplify API response handling`

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

## Project Structure

```
Prompt-Boost/
├── backend/           # FastAPI backend
│   ├── main.py       # API routes
│   ├── database.py   # Database operations
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/          # React components
│   └── package.json
├── docs/             # Documentation
└── .github/          # GitHub workflows
```

## Questions?

Open an issue for bugs, feature requests, or questions.

## License

By contributing, you agree that your contributions will be licensed under the GPL-3.0 License.
