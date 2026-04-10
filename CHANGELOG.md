# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-10

### Added
- TypeScript support for frontend
- Docker and docker-compose configuration
- GitHub Actions CI/CD pipeline
- Rate limiting (30 requests/minute per IP)
- CONTRIBUTING.md and CHANGELOG.md
- Comprehensive README.md documentation

### Changed
- API Key now configured via environment variable (security improvement)
- CORS configured via environment variable
- Backend code refactored with lifespan context manager
- Enhanced prompt validation and sanitization
- Pydantic models with field validators

### Fixed
- Security issue: API Key no longer exposed in frontend
- Input validation for empty prompts
- Error handling improvements

## [1.0.0] - 2025-08-24

### Added
- Initial release
- Prompt improvement using GPT-4o
- Visual diff display
- Prompt sharing system
- Public gallery
- FastAPI backend with SQLite
- React frontend

### Features
- Original prompt input
- Improved prompt output with diff view
- Share prompts with unique URLs
- Publish to public gallery
- Copy to clipboard functionality
