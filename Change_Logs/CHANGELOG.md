# Changelog

## [2024-03-02] Portfolio Template Update

### Files Affected
- `/src/templates/portfolio.html`

### Changes Made
- Enhanced portfolio template with improved styling and layout
- Added YourAIVoiceJournal project with proper styling and metadata
- Implemented responsive grid layout for project cards
- Added SecureLogRedactor project as a second portfolio item
- Improved accessibility with proper semantic HTML and ARIA attributes
- Added dark mode support with appropriate color schemes

### Reason for Change
To improve the visual presentation and maintainability of the portfolio section while ensuring proper display of project information.

## [2024-01-09] Portfolio URL Fix

### Files Affected
- `src/generator/site_generator.py`

### Changes Made
- Modified the `url_for` function to handle the portfolio page URL specifically
- Updated to return `portfolio.html` instead of a directory-style URL

### Reason for Change
To fix the portfolio page URL structure, ensuring it's accessible at `/portfolio.html` instead of `/portfolio/`

## [2024-01-09] Portfolio Page Generation Update

### Files Affected
- `src/generator/site_generator.py`

### Changes Made
- Modified portfolio page generation to write directly to output directory

### Reason for Change
Simplified URL structure by placing portfolio.html at root instead of in subdirectory
