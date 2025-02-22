# Changelog

All notable changes to JimiLand will be documented in this file.

## [2025-02-22]

### Added
- Implemented proper URL handling for custom domain (jimi.land)
- Added new `url_for` function for consistent URL generation
- Added security attributes to portfolio links
- Created logging structure and documentation practices

### Changed
- Updated base URL configuration to support custom domain
- Modified navigation links to use new URL generation system
- Updated portfolio links to open in new tabs with security attributes

### Security
- Added rel="noopener noreferrer" to external links
- Moved API keys to GitHub Secrets

### Files Affected
- src/generator/site_generator.py
- src/templates/base.html
- src/templates/portfolio.html
- src/templates/post.html
- .github/workflows/deploy.yml

### Technical Debt
- Need to implement image optimization
- Need to add proper error handling
- Need to improve test coverage
