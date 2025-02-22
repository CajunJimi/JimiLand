"""
Notion content processor module.
Handles converting Notion blocks into HTML content.

This module processes various types of Notion blocks including:
- Text blocks (paragraphs, headings)
- Lists (bulleted, numbered)
- Media (images, videos)
- Embeds (YouTube, websites)
- Code blocks
- Quotes and callouts
"""

import re
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

class NotionProcessor:
    """
    Processes Notion blocks and converts them to HTML.
    Handles rich text formatting, links, and various block types.
    """

    def __init__(self):
        """Initialize the processor with block type handlers."""
        # Map Notion block types to their handler methods
        self.block_handlers = {
            'paragraph': self._process_paragraph,
            'heading_1': self._process_heading,
            'heading_2': self._process_heading,
            'heading_3': self._process_heading,
            'bulleted_list_item': self._process_list_item,
            'numbered_list_item': self._process_list_item,
            'code': self._process_code,
            'quote': self._process_quote,
            'callout': self._process_callout,
            'image': self._process_image,
            'video': self._process_video,
            'embed': self._process_embed,
            'bookmark': self._process_bookmark,
            'link_preview': self._process_link_preview,
        }

    def process_blocks(self, blocks: List[Dict]) -> str:
        """
        Process a list of Notion blocks into HTML.
        
        Args:
            blocks: List of Notion block objects
            
        Returns:
            HTML string
        """
        html_parts = []
        in_list = False
        list_type = None
        
        # Check if this is a letter format
        is_letter = any('HST - Letter' in block.get('heading_1', {}).get('rich_text', [{}])[0].get('text', {}).get('content', '') 
                       for block in blocks if block['type'] == 'heading_1')
        
        if is_letter:
            # Extract letter metadata
            date = None
            address = []
            salutation = None
            body_started = False
            body_parts = []
            
            for block in blocks:
                if block['type'] == 'paragraph':
                    text = self._get_text_content(block['paragraph']['rich_text'])
                    if not date and re.match(r'\d{4}-\d{2}-\d{2}', text):
                        date = text
                    elif not salutation and text.startswith('Dear '):
                        salutation = text
                    elif not body_started and text.strip():
                        if not salutation:
                            address.append(text)
                        else:
                            body_started = True
                            body_parts.append(f'<p>{text}</p>')
                    elif body_started:
                        body_parts.append(f'<p>{text}</p>')
                        
            # Structure letter HTML
            html_parts.append('<div class="letter">')
            if date:
                html_parts.append(f'<div class="letter-date">{date}</div>')
            if address:
                html_parts.append('<div class="letter-address">')
                html_parts.extend(f'<div>{line}</div>' for line in address)
                html_parts.append('</div>')
            if salutation:
                html_parts.append(f'<div class="letter-salutation">{salutation}</div>')
            html_parts.append('<div class="letter-body">')
            html_parts.extend(body_parts)
            html_parts.append('</div>')
            html_parts.append('</div>')
            
        else:
            # Regular content processing
            for block in blocks:
                block_type = block['type']
                if block_type in self.block_handlers:
                    handler = self.block_handlers[block_type]
                    html = handler(block)
                    
                    if block_type in ['bulleted_list_item', 'numbered_list_item']:
                        if not in_list or list_type != block_type:
                            if in_list:
                                html_parts.append(self._end_list(list_type))
                            html_parts.append(self._start_list(block_type))
                            in_list = True
                            list_type = block_type
                    else:
                        if in_list:
                            html_parts.append(self._end_list(list_type))
                            in_list = False
                            list_type = None
                            
                    html_parts.append(html)
                    
            if in_list:
                html_parts.append(self._end_list(list_type))
                
        return '\n'.join(html_parts)

    def _process_rich_text(self, rich_text: List[Dict]) -> str:
        """
        Process Notion's rich text array into HTML with proper formatting.
        
        Args:
            rich_text: List of Notion rich text objects
            
        Returns:
            str: HTML formatted text
        """
        if not rich_text:
            return ''

        result = []
        for text in rich_text:
            try:
                content = text.get('text', {}).get('content', '')
                link = text.get('text', {}).get('link')
                annotations = text.get('annotations', {})

                # Apply text formatting
                if annotations.get('code'):
                    content = f'<code>{content}</code>'
                if annotations.get('bold'):
                    content = f'<strong>{content}</strong>'
                if annotations.get('italic'):
                    content = f'<em>{content}</em>'
                if annotations.get('strikethrough'):
                    content = f'<del>{content}</del>'
                if annotations.get('underline'):
                    content = f'<u>{content}</u>'

                # Handle links
                if link:
                    content = f'<a href="{link["url"]}" target="_blank" rel="noopener noreferrer">{content}</a>'

                result.append(content)
            except Exception as e:
                print(f"Error processing rich text: {str(e)}")
                continue

        return ''.join(result)

    def _process_paragraph(self, block: Dict) -> str:
        """Convert Notion paragraph block to HTML paragraph."""
        text = self._process_rich_text(block['paragraph']['rich_text'])
        return f'<p>{text}</p>' if text else '<p></p>'

    def _process_heading(self, block: Dict) -> str:
        """Convert Notion heading block to HTML heading."""
        level = int(block['type'][-1])  # Extract heading level from type
        text = self._process_rich_text(block[block['type']]['rich_text'])
        return f'<h{level}>{text}</h{level}>'

    def _process_list_item(self, block: Dict) -> str:
        """Convert Notion list item block to HTML list item."""
        text = self._process_rich_text(block[block['type']]['rich_text'])
        return f'<li>{text}</li>'

    def _start_list(self, list_type: str) -> str:
        """Return opening tag for a list."""
        return '<ul>' if list_type == 'bulleted_list_item' else '<ol>'

    def _end_list(self, list_type: str) -> str:
        """Return closing tag for a list."""
        return '</ul>' if list_type == 'bulleted_list_item' else '</ol>'

    def _process_code(self, block: Dict) -> str:
        """Convert Notion code block to HTML code block."""
        code = self._process_rich_text(block['code']['rich_text'])
        language = block['code'].get('language', '')
        return f'<pre><code class="language-{language}">{code}</code></pre>'

    def _process_quote(self, block: Dict) -> str:
        """Convert Notion quote block to HTML blockquote."""
        text = self._process_rich_text(block['quote']['rich_text'])
        return f'<blockquote>{text}</blockquote>'

    def _process_callout(self, block: Dict) -> str:
        """Convert Notion callout block to styled HTML div."""
        text = self._process_rich_text(block['callout']['rich_text'])
        icon = block['callout'].get('icon', {}).get('emoji', 'ℹ️')
        return f'<div class="callout"><span class="callout-icon">{icon}</span>{text}</div>'

    def _process_image(self, block: Dict) -> str:
        """Convert Notion image block to HTML img tag."""
        image = block['image']
        url = image.get('file', {}).get('url') or image.get('external', {}).get('url')
        caption = self._process_rich_text(image.get('caption', []))
        if url:
            return f'<figure><img src="{url}" alt="{caption}"/>{caption and f"<figcaption>{caption}</figcaption>"}</figure>'
        return ''

    def _process_video(self, block: Dict) -> str:
        """Convert Notion video block to HTML video or iframe."""
        video = block['video']
        url = video.get('file', {}).get('url') or video.get('external', {}).get('url')
        
        if not url:
            return ''

        # Handle YouTube videos
        if 'youtube.com' in url or 'youtu.be' in url:
            video_id = self._extract_youtube_id(url)
            if video_id:
                return f'<div class="video-container"><iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe></div>'

        # Default video player for other videos
        return f'<video controls><source src="{url}" type="video/mp4">Your browser does not support the video tag.</video>'

    def _process_embed(self, block: Dict) -> str:
        """Convert Notion embed block to HTML iframe."""
        url = block['embed'].get('url')
        if url:
            return f'<div class="embed-container"><iframe src="{url}" frameborder="0" allowfullscreen></iframe></div>'
        return ''

    def _process_bookmark(self, block: Dict) -> str:
        """Convert Notion bookmark block to styled link card."""
        url = block['bookmark'].get('url')
        caption = self._process_rich_text(block['bookmark'].get('caption', []))
        domain = urlparse(url).netloc
        
        bookmark_html = f'<a href="{url}" class="bookmark" target="_blank" rel="noopener noreferrer">'
        bookmark_html += '<div class="bookmark-info">'
        bookmark_html += f'<div class="bookmark-domain">{domain}</div>'
        if caption:
            bookmark_html += f'<div class="bookmark-caption">{caption}</div>'
        bookmark_html += '</div></a>'
        
        return bookmark_html

    def _process_link_preview(self, block: Dict) -> str:
        """Convert Notion link preview block to styled link card."""
        url = block['link_preview'].get('url')
        if url:
            domain = urlparse(url).netloc
            return f'<a href="{url}" class="link-preview" target="_blank" rel="noopener noreferrer"><div class="link-preview-domain">{domain}</div></a>'
        return ''

    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            if match := re.search(pattern, url):
                return match.group(1)
        return None

    def _get_text_content(self, rich_text: List[Dict]) -> str:
        """
        Process Notion's rich text array into plain text.
        
        Args:
            rich_text: List of Notion rich text objects
            
        Returns:
            str: Plain text
        """
        if not rich_text:
            return ''

        result = []
        for text in rich_text:
            try:
                content = text.get('text', {}).get('content', '')
                result.append(content)
            except Exception as e:
                print(f"Error processing rich text: {str(e)}")
                continue

        return ''.join(result)
