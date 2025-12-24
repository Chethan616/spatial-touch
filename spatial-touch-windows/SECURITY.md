# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within Spatial Touch, please send an email to security@spatialtouch.dev. All security vulnerabilities will be promptly addressed.

Please include the following information:
- Type of issue (e.g., buffer overflow, privilege escalation, etc.)
- Full paths of source file(s) related to the issue
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue

## Security Measures

### Privacy by Design

- **No Cloud**: All processing happens locally on your device
- **No Storage**: Camera frames are processed in memory and immediately discarded
- **No Transmission**: No network activity or data collection
- **Open Source**: Full transparency of code for security auditing

### Application Security

- Uses Windows native APIs for input injection
- No elevated privileges required
- Minimal attack surface (no network, no file I/O except logs)
- PyAutoGUI failsafe enabled (move mouse to corner to abort)

### Best Practices

When using Spatial Touch:
- Keep your system and Python packages updated
- Download only from official sources (GitHub releases)
- Verify file hashes when available
- Review configuration files before use

## Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who help improve Spatial Touch.
