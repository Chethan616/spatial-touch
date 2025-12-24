# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- Camera capture module with OpenCV
- Hand tracking with MediaPipe Hands
- Gesture detection engine (pinch, click, drag)
- Zone mapper for screen coordinate mapping
- Action dispatcher for OS input injection
- Exponential moving average smoothing
- Configuration system (JSON-based)
- Logging infrastructure
- Unit tests for core modules

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.0] - 2024-XX-XX (Planned)

### Added
- Core MVP features:
  - Cursor control via index finger
  - Left click (thumb-index pinch)
  - Right click (thumb-middle pinch)
  - Drag and drop
- Basic configuration support
- Command-line interface
- Debug mode with visual feedback

---

## Versioning Guidelines

- **MAJOR**: Breaking changes to the API or configuration format
- **MINOR**: New features that are backwards compatible
- **PATCH**: Bug fixes and minor improvements

## Release Process

1. Update version in `pyproject.toml` and `src/spatial_touch/__init__.py`
2. Update this CHANGELOG with release notes
3. Create a git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions will build and release
