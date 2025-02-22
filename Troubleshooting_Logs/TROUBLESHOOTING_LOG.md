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
