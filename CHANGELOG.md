# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-04-10

### Added
- Settings page for API configuration
- Endpoints: GET/POST /api/config, POST /api/config/test
- Support for: API Key, CORS Origins, Rate Limit, Model, Temperature, Max Tokens
- Configuration stored in .env file (runtime updates)
- Test API key functionality with visual feedback
- Toggle to show/hide API key
- Portuguese localization for settings page

### Changed
- API key now configured via settings page (not environment variable)
- Backend version to 1.2.0
- Updated docker-compose.yml (removed hardcoded environment variables)
- Improved error messages in Portuguese

## [1.2.0] - 2026-04-10

### Added
- Complete UI/UX redesign with modern dark theme
- Gradient backgrounds and smooth animations
- Responsive design for mobile devices
- Custom typography (Inter + JetBrains Mono fonts)
- Toast notifications with animations
- Enhanced diff display with color highlighting
- Portuguese localization for all UI text

### Changed
- Updated color palette (Indigo/Purple theme)
- Improved loading spinner animations
- Better card hover effects with shadows
- Gallery page with improved cards
- SEO meta tags in index.html

### Fixed
- Fixed API URL in GalleryPage (use env variable)
- Fixed diff display empty state
- Fixed loading spinner text

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
