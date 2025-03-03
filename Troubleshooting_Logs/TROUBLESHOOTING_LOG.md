# Troubleshooting Log

## [2025-02-22] Navigation Links Not Working with Custom Domain

### Issue Description
After setting up the custom domain (jimi.land), navigation links were not working correctly. Links were being generated with an incorrect base URL, causing 404 errors.

### Investigation
1. Checked GitHub Pages configuration
2. Reviewed URL generation in templates
3. Analyzed site_generator.py URL handling

### Root Cause
The site generator was using a hardcoded base URL that didn't account for the custom domain setup.

### Resolution Steps
1. Updated site_generator.py to use environment-based base URL
2. Added new url_for function for consistent URL generation
3. Modified templates to use the new URL generation system
4. Updated GitHub Actions workflow with correct base URL

### Outcome
- Navigation links now work correctly with the custom domain
- All internal links are properly generated
- Portfolio links open in new tabs with security attributes

### Prevention
- Added URL generation tests
- Implemented proper base URL configuration
- Added documentation for URL handling

## [2025-02-22] Portfolio Links Security Enhancement

### Issue Description
Portfolio links were opening in the same tab and lacked security attributes for external links.

### Resolution Steps
1. Added target="_blank" to open links in new tabs
2. Implemented rel="noopener noreferrer" for security
3. Updated portfolio template

### Outcome
- Links now open safely in new tabs
- Protected against potential security vulnerabilities

## [2025-03-03] Portfolio Page Not Accessible

### Issue Description
The portfolio page was not being properly deployed to the live site. The URL `https://jimi.land/portfolio/` was showing but not displaying the updated content with YourAIVoiceJournal project.

### Resolution Steps
1. Analyzed site generator code and found that portfolio page was being generated in a subdirectory (`portfolio/index.html`)
2. Modified site generator to write portfolio page directly to output directory as `portfolio.html`
3. Updated URL generation in the `url_for` function to correctly link to `portfolio.html`
4. Added direct HTML file approach as a fallback:
   - Created a standalone HTML file with portfolio content
   - Modified GitHub Actions workflow to copy this file directly to the output directory
   - This ensures the content is accessible regardless of site generator configuration

### Outcome
The portfolio page should now be accessible at both `https://jimi.land/portfolio.html` and `https://jimi.land/portfolio/` with the updated content showing YourAIVoiceJournal project.

## [2025-03-03 20:40] Portfolio Page Not Accessible - Follow-up

### Issue Description
Previous attempts to fix the portfolio page accessibility issue were unsuccessful. The page at `https://jimi.land/portfolio/` was still not showing the updated content with YourAIVoiceJournal project, even after implementing direct HTML file approach.

### Resolution Steps
1. Created a dedicated `portfolio-index.html` file with the complete portfolio content
2. Modified GitHub Actions workflow to:
   - Create a `portfolio` directory in the output
   - Copy the `portfolio-index.html` file to `output/portfolio/index.html`
3. This approach aligns with GitHub Pages' URL routing behavior, which looks for `index.html` files in directories

### Outcome
The portfolio page should now be accessible at `https://jimi.land/portfolio/` with the updated content showing YourAIVoiceJournal project. This approach creates the exact file structure that GitHub Pages expects for directory-based URLs.
