"""
Static site generator for Notion-based blog.

This module handles:
1. Fetching content from Notion
2. Processing Notion blocks into HTML
3. Generating static site files using templates
4. Managing assets and media files

Key components:
- NotionClient: Handles API communication with Notion
- NotionProcessor: Converts Notion blocks to HTML
- SiteGenerator: Manages the static site generation process
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from notion_client import Client
from jinja2 import Environment, FileSystemLoader
from ..notion.processor import NotionProcessor
from urllib.parse import quote
from ..spotify.spotify import get_current_track
import logging
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/site_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def date_filter(date_str):
    """Convert date string to formatted date"""
    if isinstance(date_str, str):
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%B %d, %Y')
        except ValueError:
            return date_str
    return date_str

class SiteGenerator:
    """
    Main class for generating static site from Notion content.
    Handles content fetching, processing, and file generation.
    """

    def __init__(self, output_dir: str, template_dir: str):
        """Initialize the site generator with improved error handling."""
        try:
            # Load environment variables
            load_dotenv()
            
            # Initialize Notion client and processor
            notion_api_key = os.getenv('NOTION_API_KEY')
            if not notion_api_key:
                raise ValueError("NOTION_API_KEY environment variable is not set")
            
            self.notion = Client(auth=notion_api_key)
            self.processor = NotionProcessor()
            
            # Set up paths
            self.output_dir = Path(output_dir)
            self.template_dir = Path(template_dir)
            
            # Create necessary directories
            self.output_dir.mkdir(parents=True, exist_ok=True)
            (self.output_dir / 'static').mkdir(parents=True, exist_ok=True)
            
            # Initialize Jinja environment
            self._setup_jinja_env()
            
            # Site configuration
            self.site_config = self._load_site_config()
            
            logger.info("SiteGenerator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SiteGenerator: {str(e)}")
            raise

    def _setup_jinja_env(self):
        """Initialize Jinja environment."""
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
        
        # Add custom filters
        self.jinja_env.filters['date'] = date_filter
        
        # Add reading time filter
        self.jinja_env.filters['reading_time'] = self._calculate_reading_time

        # Add static_url function
        def static_url(filename):
            base_url = self.site_config['base_url']
            return f"{base_url}/static/{filename.lstrip('/')}"
        self.jinja_env.globals['static_url'] = static_url
        
        # Add url_for function for generating URLs
        def url_for(path):
            base_url = self.site_config['base_url']
            if path == 'portfolio':
                return f"{base_url}/portfolio.html"
            return f"{base_url}/{path.lstrip('/')}"
        self.jinja_env.globals['url_for'] = url_for

    def _load_site_config(self) -> Dict:
        """Load site configuration."""
        return {
            'title': 'Jimi Land',
            'description': 'A personal website about music, life, and adventures',
            'author': 'Josh Brown',
            'base_url': os.getenv('SITE_BASE_URL', '')  # Get base URL from environment
        }

    def optimize_image(self, image_path: str, max_width: int = 1200) -> str:
        """
        Optimize an image by resizing and compressing it, with caching.
        
        Args:
            image_path: Path to the image file
            max_width: Maximum width for the image
            
        Returns:
            Path to the optimized image
        """
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Check if optimized version exists and is newer than original
            optimized_path = image_path.parent / f"{image_path.stem}.optimized{image_path.suffix}"
            if optimized_path.exists() and optimized_path.stat().st_mtime > image_path.stat().st_mtime:
                logger.info(f"Using cached optimized image: {optimized_path}")
                return str(optimized_path)
                
            with Image.open(image_path) as img:
                # Calculate new dimensions
                ratio = max_width / img.width if img.width > max_width else 1
                new_size = (int(img.width * ratio), int(img.height * ratio))
                
                # Only resize if necessary
                if ratio < 1:
                    img = img.resize(new_size, Image.LANCZOS)
                
                # Save with optimization
                img.save(
                    optimized_path,
                    quality=85,
                    optimize=True,
                    progressive=True
                )
                
                logger.info(f"Created optimized image: {image_path} -> {optimized_path}")
                return str(optimized_path)
                
        except Exception as e:
            logger.error(f"Failed to optimize image {image_path}: {str(e)}")
            return str(image_path)  # Return original path on failure

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _fetch_notion_data(self, page_id: str) -> Dict:
        """
        Fetch data from Notion with retry logic.
        
        Args:
            page_id: Notion page ID
            
        Returns:
            Dictionary containing page data
        """
        try:
            response = self.notion.pages.retrieve(page_id=page_id)
            logger.info(f"Successfully fetched Notion page: {page_id}")
            return response
        except Exception as e:
            logger.error(f"Error fetching Notion page {page_id}: {str(e)}")
            raise

    def _process_images(self, content: str) -> str:
        """
        Process and optimize images in content.
        
        Args:
            content: HTML content containing images
            
        Returns:
            Updated content with optimized images
        """
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(content, 'html.parser')
            for img in soup.find_all('img'):
                src = img.get('src')
                if src and src.startswith('/static/'):
                    # Optimize image and update src
                    original_path = self.output_dir / src.lstrip('/')
                    optimized_path = self.optimize_image(original_path)
                    img['src'] = f"/static/{Path(optimized_path).name}"
                    # Add lazy loading
                    img['loading'] = 'lazy'
                    
            return str(soup)
            
        except Exception as e:
            logger.error(f"Error processing images: {str(e)}")
            return content

    def _calculate_reading_time(self, content: str) -> str:
        """
        Calculate estimated reading time for an article.
        
        Args:
            content: The article content in HTML format
            
        Returns:
            String with estimated reading time (e.g., "5 min read")
        """
        # Average reading speed (words per minute)
        WPM = 200
        
        # Remove HTML tags and split into words
        # This is a simple approach - for more accuracy you might want to use BeautifulSoup
        words = content.replace('<', ' <').replace('>', '> ').split()
        word_count = len(words)
        
        # Calculate reading time in minutes
        minutes = max(1, round(word_count / WPM))
        
        return f"{minutes} min read"

    def generate_site(self):
        """
        Generate the complete static site.
        """
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get and process all articles
        articles = self._get_articles()
        
        # Generate individual article pages
        for article in articles:
            self._generate_article_page(article)
        
        # Generate pages
        self._generate_index_page(articles)
        self._generate_archive_page(articles)
        self._generate_gigs_page()
        self._generate_about_page()
        self._generate_portfolio_page()
        self._copy_static_files()

    def _get_articles(self) -> List[Dict]:
        """
        Fetch and process all articles from Notion.
        
        Returns:
            List of processed article dictionaries
        """
        articles = []
        
        try:
            # Query the database
            response = self.notion.databases.query(
                database_id=os.getenv('NOTION_DATABASE_ID'),
            )
            print(f"\nDatabase query response: {response}")
            
            # Process each page
            for page in response.get('results', []):
                print(f"\nProcessing page: {page.get('id')}")
                if article := self._process_article(page):
                    articles.append(article)
                    
        except Exception as e:
            print(f"Error fetching articles: {str(e)}")
            
        return articles

    def _process_article(self, page: Dict) -> Optional[Dict]:
        """Process a single Notion page into an article."""
        try:
            # Extract basic metadata
            properties = page['properties']
            
            # Get title (required)
            title_prop = properties.get('Title', {}).get('title', [{}])
            if not title_prop:
                return None
            title = title_prop[0].get('plain_text', 'Untitled')
            
            # Get date (optional)
            date_prop = properties.get('Date', {}).get('date', {})
            date = date_prop.get('start') if date_prop else datetime.now().strftime('%Y-%m-%d')
            
            # Get description (optional)
            desc_prop = properties.get('Description', {}).get('rich_text', [{}])
            description = desc_prop[0].get('plain_text', '') if desc_prop else ''
            
            # Get tags (optional)
            tags = [tag['name'] for tag in properties.get('Tags', {}).get('multi_select', [])]
            
            # Generate URL-friendly slug
            slug = self._generate_slug(title)
            
            # Fetch and process content blocks
            blocks = self._get_page_blocks(page['id'])
            content_html = self.processor.process_blocks(blocks)
            
            return {
                'id': page['id'],
                'title': title,
                'date': date,
                'description': description,
                'tags': tags,
                'slug': slug,
                'content_html': content_html
            }
            
        except Exception as e:
            print(f"Error processing article {page.get('id')}: {str(e)}")
            return None

    def _get_page_blocks(self, page_id: str) -> List[Dict]:
        """
        Fetch all blocks for a Notion page.
        
        Args:
            page_id: ID of the Notion page
            
        Returns:
            List of Notion blocks
        """
        blocks = []
        
        try:
            # Get the content URL from the page properties
            content_prop = self.notion.pages.retrieve(page_id=page_id).get('properties', {}).get('Content', {}).get('rich_text', [])
            if not content_prop:
                return blocks
                
            # Extract the page ID from the content URL
            content_url = content_prop[0].get('text', {}).get('content', '')
            content_id = content_url.split('-')[-1].split('?')[0]
            
            print(f"Fetching content from page: {content_id}")
            
            # Fetch blocks from the actual content page
            response = self.notion.blocks.children.list(block_id=content_id)
            blocks.extend(response.get('results', []))
            
            # Handle pagination
            while response.get('has_more'):
                response = self.notion.blocks.children.list(
                    block_id=content_id,
                    start_cursor=response.get('next_cursor')
                )
                blocks.extend(response.get('results', []))
                
        except Exception as e:
            print(f"Error getting blocks: {str(e)}")
            
        return blocks

    def _generate_slug(self, title: str) -> str:
        """
        Generate URL-friendly slug from article title.
        
        Args:
            title: Article title
            
        Returns:
            URL-friendly slug
        """
        # Replace spaces with hyphens and remove special characters
        slug = title.lower().replace(' ', '-')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        
        # Ensure URL-safe encoding
        return quote(slug)

    def _generate_article_page(self, article: Dict):
        """
        Generate HTML page for a single article.
        
        Args:
            article: Processed article dictionary
        """
        template = self.jinja_env.get_template('post.html')
        output = self.render_template('post.html', {
            'site_title': self.site_config['title'],
            'site_description': self.site_config['description'],
            'site_author': self.site_config['author'],
            'site_base_url': self.site_config['base_url'],
            'article': article,
            'current_year': datetime.now().year
        })
        
        # Create article directory and write HTML
        article_dir = self.output_dir / 'posts' / article['slug']
        article_dir.mkdir(parents=True, exist_ok=True)
        
        with open(article_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(output)

    def render_template(self, template_name: str, context: Dict) -> str:
        """Render a template with the given context."""
        template = self.jinja_env.get_template(template_name)
        
        # Add Spotify data to context only if credentials are available
        try:
            spotify_context = context.copy()
            current_track = get_current_track()
            if current_track:
                spotify_context['current_track'] = current_track
            return template.render(**spotify_context)
        except Exception as e:
            print(f"Error adding Spotify data: {e}")
            return template.render(**context)

    def _generate_index_page(self, articles: List[Dict] = None):
        """
        Generate site index page with article previews.
        
        Args:
            articles: List of processed articles
        """
        if articles is None:
            articles = self._get_articles()

        # Sort articles by date (newest first)
        articles.sort(key=lambda x: x['date'], reverse=True)

        # Generate the page
        template = self.jinja_env.get_template('index.html')
        output = self.render_template('index.html', {
            'site_title': self.site_config['title'],
            'site_description': self.site_config['description'],
            'site_author': self.site_config['author'],
            'site_base_url': self.site_config['base_url'],
            'articles': articles
        })

        # Write the file
        with open(self.output_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(output)

    def _generate_gigs_page(self):
        """Generate the gigs page from Notion database.
        
        This function fetches gig data from a Notion database and generates both a list view
        and a calendar view of all gigs. The Notion database should have the following properties:
        
        Required Properties:
        - Gig (Title): A unique identifier for each gig
        - Date (Date): When the gig took place
        - Artist (Rich Text): Name of the artist/band
        - Venue (Rich Text): Name of the venue
        
        Optional Properties:
        - location (Rich Text): Location of the venue (defaults to venue name if not specified)
        - Notes (Rich Text): Any additional notes about the gig
        - Setlist (URL): Link to the setlist (e.g., from setlist.fm)
        """
        # Reload environment variables to ensure we have the latest values
        load_dotenv(override=True)
        
        # Fetch gigs from Notion
        gigs_db_id = os.getenv('NOTION_GIGS_DATABASE_ID')
        if not gigs_db_id:
            print("Warning: NOTION_GIGS_DATABASE_ID not set, skipping gigs page generation")
            return

        try:
            print(f"Generating gigs page from database: {gigs_db_id}")
            # Query the gigs database, sorting by date in descending order
            response = self.notion.databases.query(
                database_id=gigs_db_id,
                sorts=[{
                    "property": "Date",
                    "direction": "descending"
                }]
            )

            # Initialize data structures for processing gigs
            gigs = []  # List to store all processed gigs
            venues = set()  # Set of unique venues
            artists = set()  # Set of unique artists
            locations = set()  # Set of unique locations
            calendar_events = []  # List for calendar view events
            gig_counter = 1  # Counter for generating fallback IDs

            # Process each gig from the database
            for page in response['results']:
                try:
                    # Get or generate a unique ID for the gig
                    gig_id = str(gig_counter)
                    if (page['properties']['Gig']['title'] and 
                        len(page['properties']['Gig']['title']) > 0):
                        gig_id = page['properties']['Gig']['title'][0]['text']['content']
                    gig_counter += 1

                    # Extract gig information
                    gig = {'id': gig_id}
                    
                    # Get required Date property
                    if page['properties']['Date'].get('date'):
                        gig['date'] = page['properties']['Date']['date']['start']
                        gig['year'] = gig['date'][:4]  # Extract year for grouping
                    else:
                        print(f"Skipping gig {gig_id}: Missing date")
                        continue

                    # Get required Artist property
                    artist_prop = page['properties']['Artist']
                    if artist_prop.get('rich_text') and artist_prop['rich_text']:
                        gig['artist'] = artist_prop['rich_text'][0]['text']['content']
                    else:
                        print(f"Skipping gig {gig_id}: Missing artist")
                        continue

                    # Get required Venue property
                    venue_prop = page['properties']['Venue']
                    if venue_prop.get('rich_text') and venue_prop['rich_text']:
                        gig['venue'] = venue_prop['rich_text'][0]['text']['content']
                    else:
                        print(f"Skipping gig {gig_id}: Missing venue")
                        continue

                    # Get optional location property (defaults to venue)
                    location_prop = page['properties'].get('location', {})
                    if location_prop.get('rich_text') and location_prop['rich_text']:
                        gig['location'] = location_prop['rich_text'][0]['text']['content']
                    else:
                        gig['location'] = gig['venue']  # Use venue as location if not specified

                    # Get optional Notes property
                    notes_prop = page['properties'].get('Notes', {})
                    if notes_prop.get('rich_text') and notes_prop['rich_text']:
                        gig['notes'] = notes_prop['rich_text'][0]['text']['content']

                    # Get optional Setlist property
                    setlist_prop = page['properties'].get('Setlist', {})
                    if setlist_prop.get('url'):
                        gig['setlist_url'] = setlist_prop['url']

                    # Add gig to our collections
                    gigs.append(gig)
                    venues.add(gig['venue'])
                    artists.add(gig['artist'])
                    locations.add(gig['location'])

                    # Create calendar event for this gig
                    calendar_events.append({
                        'id': gig['id'],
                        'title': f"{gig['artist']} @ {gig['venue']}",
                        'start': gig['date'],
                        'url': gig.get('setlist_url', ''),
                        'location': gig['location']
                    })

                except Exception as e:
                    print(f"Error processing gig {gig_counter}: {str(e)}")
                    continue

            print(f"\nSuccessfully processed {len(gigs)} gigs")
            
            # Sort gigs by date (newest first)
            gigs.sort(key=lambda x: x['date'], reverse=True)

            # Group gigs by year for the list view
            gigs_by_year = {}
            for gig in gigs:
                year = gig['year']
                if year not in gigs_by_year:
                    gigs_by_year[year] = []
                gigs_by_year[year].append(gig)

            # Generate the page using our template
            template = self.jinja_env.get_template('gigs.html')
            output = self.render_template('gigs.html', {
                'site_title': self.site_config['title'],
                'site_description': self.site_config['description'],
                'site_author': self.site_config['author'],
                'site_base_url': self.site_config['base_url'],
                'gigs': gigs,  # All gigs for processing in template
                'gigs_by_year': gigs_by_year,  # Gigs grouped by year
                'years': sorted(gigs_by_year.keys(), reverse=True),  # Years for iteration
                'venues': sorted(list(venues)),  # Unique venues
                'artists': sorted(list(artists)),  # Unique artists
                'locations': sorted(list(locations)),  # Unique locations
                'calendar_events': calendar_events,  # Events for calendar view
                'total_gigs': len(gigs)  # Total number of gigs
            })

            # Write the generated HTML to file
            gigs_dir = self.output_dir / 'gigs'
            gigs_dir.mkdir(exist_ok=True)
            with open(gigs_dir / 'index.html', 'w', encoding='utf-8') as f:
                f.write(output)

            print(f"Generated gigs page with {len(gigs)} gigs")

        except Exception as e:
            print(f"Error generating gigs page: {e}")
            raise  # Re-raise to see full traceback

    def _generate_about_page(self):
        """Generate the about page."""
        try:
            # Generate the page using our template
            template = self.jinja_env.get_template('about.html')
            output = self.render_template('about.html', {
                'site_title': self.site_config['title'],
                'site_description': self.site_config['description'],
                'site_author': self.site_config['author'],
                'site_base_url': self.site_config['base_url']
            })

            # Write the file
            about_dir = self.output_dir / 'about'
            about_dir.mkdir(exist_ok=True)
            with open(about_dir / 'index.html', 'w', encoding='utf-8') as f:
                f.write(output)

            print("Generated about page")

        except Exception as e:
            print(f"Error generating about page: {e}")
            raise

    def _generate_portfolio_page(self):
        """Generate the portfolio page."""
        output = self.render_template('portfolio.html', {
            'site_title': self.site_config['title'],
            'site_description': self.site_config['description'],
            'site_author': self.site_config['author'],
            'site_base_url': self.site_config['base_url'],
            'current_year': datetime.now().year
        })
        
        # Write portfolio.html directly to the output directory
        with open(self.output_dir / 'portfolio.html', 'w', encoding='utf-8') as f:
            f.write(output)

    def _generate_archive_page(self, articles: List[Dict] = None):
        """Generate archive page with all articles."""
        if articles is None:
            articles = self._get_articles()
        
        # Sort articles by date (newest first)
        articles.sort(key=lambda x: x['date'], reverse=True)

        # Generate the page
        template = self.jinja_env.get_template('archive.html')
        output = self.render_template('archive.html', {
            'site_title': self.site_config['title'],
            'site_description': self.site_config['description'],
            'site_author': self.site_config['author'],
            'site_base_url': self.site_config['base_url'],
            'articles': articles
        })

        # Create archive directory and write the file
        archive_dir = self.output_dir / 'archive'
        archive_dir.mkdir(exist_ok=True)
        with open(archive_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(output)

    def _copy_static_files(self):
        """Copy static assets to output directory."""
        static_src = Path('src/static')
        static_dest = self.output_dir / 'static'

        # Create the static directory in output if it doesn't exist
        static_dest.mkdir(exist_ok=True)

        # Copy all files from src/static to output/static
        if static_src.exists():
            for item in static_src.glob('**/*'):
                if item.is_file():
                    # Get the relative path from src/static
                    rel_path = item.relative_to(static_src)
                    # Create the destination path
                    dest_path = static_dest / rel_path
                    # Create parent directories if they don't exist
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    # Copy the file
                    shutil.copy2(item, dest_path)


if __name__ == "__main__":
    # Create and run the site generator
    generator = SiteGenerator('output', 'src/templates')
    generator.generate_site()
