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

## [2025-03-02] Added LiveTranscript Project to Portfolio

### Files Affected
- `src/templates/portfolio.html`

### Changes Made
- Added LiveTranscript project to the portfolio page
- Included project description, technologies (TypeScript, React, Web Speech API), and link

### Reason for Change
To showcase the new LiveTranscript project in the portfolio section

## [2025-03-02] Fixed Portfolio Template

### Files Affected
- `src/templates/portfolio.html`

### Changes Made
- Reverted back to original portfolio layout with YourAIVoiceJournal and SecureLogRedactor projects
- Removed incorrectly added LiveTranscript project

### Reason for Change
To maintain consistency with the original portfolio design and focus on the correct projects

## [2025-03-03] Fixed Portfolio Page Deployment

### Files Affected
- `src/generator/site_generator.py`

### Changes Made
- Modified portfolio page generation to write directly to output directory as portfolio.html
- Updated url_for function to correctly link to portfolio.html
- Fixed navigation to ensure portfolio page is accessible

### Reason for Change
To ensure the portfolio page is properly deployed and accessible on the live site

## [2025-03-03] Added Direct Portfolio File to Build Process

### Files Affected
- `.github/workflows/deploy.yml`

### Changes Made
- Added step in GitHub Actions workflow to directly copy the portfolio template to the output directory
- Created an additional portfolio-direct.html file that can be accessed directly

### Reason for Change
To ensure portfolio content is accessible regardless of site generator configuration

## [2025-03-03 20:40] Portfolio Page Fix - Alternative Approach

### Description
Implemented a more direct approach to fix the portfolio page accessibility issue by creating a dedicated index.html file in the portfolio directory.

### Files Affected
- `.github/workflows/deploy.yml`
- `portfolio-index.html` (new file)

### Reason for Change
Previous attempts to fix the portfolio page were unsuccessful. This approach creates a dedicated portfolio directory with an index.html file, which aligns with GitHub Pages' URL routing behavior. This should ensure the portfolio page is accessible at https://jimi.land/portfolio/ regardless of site generator configuration.
