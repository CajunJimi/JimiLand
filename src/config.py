"""
Configuration settings for the static site generator.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory paths
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_DIR = BASE_DIR / "src" / "templates"
OUTPUT_DIR = BASE_DIR / "output"
STATIC_DIR = BASE_DIR / "static"

# Notion settings
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not NOTION_API_KEY or not NOTION_DATABASE_ID:
    raise ValueError(
        "Missing required environment variables. "
        "Please ensure NOTION_API_KEY and NOTION_DATABASE_ID are set in your .env file."
    )

# Site settings
SITE_TITLE = "Jimi Land"
SITE_DESCRIPTION = "Personal blog powered by Notion"
SITE_AUTHOR = "Josh Brown"

# Use environment variable for base URL, with empty default for custom domain
SITE_BASE_URL = os.getenv('SITE_BASE_URL', '')
SITE_URL = f"https://jimi.land{SITE_BASE_URL}"

# Blog settings
POSTS_PER_PAGE = 10
DATE_FORMAT = "%B %d, %Y"

# Required Notion database properties
NOTION_PROPERTIES = {
    'title': 'title',
    'slug': 'slug',
    'date': 'date',
    'tags': 'tag',
    'description': 'description',
    'published': 'published',
    'content': 'content'
}
