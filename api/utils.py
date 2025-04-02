from bs4 import BeautifulSoup
import hashlib
import re
import json
from api import logger

def extract_text(html_content, max_length=None):
    """Extract plain text from HTML content"""
    try:
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "noscript", "iframe", "svg"]):
            script.extract()
        
        # Get text with better spacing
        lines = []
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div', 'span']):
            text = element.get_text(strip=True)
            if text:
                lines.append(text)
        
        # Join lines with newlines for better readability
        text = '\n'.join(lines)
        
        # Clean up excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit length if specified
        if max_length and len(text) > max_length:
            text = text[:max_length] + "..."
            
        return text
    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}")
        return "Error extracting text"

def extract_links(html_content, base_url=None):
    """Extract links from HTML content"""
    try:
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Skip empty, javascript, and anchor links
            if not href or href.startswith('javascript:') or href == '#':
                continue
                
            # Get link text or alt text or title
            text = a_tag.get_text(strip=True)
            if not text:
                # Try to get alt text from child img
                img = a_tag.find('img')
                if img and img.get('alt'):
                    text = img.get('alt')
                # Try to get title
                elif a_tag.get('title'):
                    text = a_tag.get('title')
                else:
                    text = href
            
            # Normalize URL if base_url is provided
            if base_url and not (href.startswith('http://') or href.startswith('https://')):
                if href.startswith('/'):
                    # Absolute path
                    from urllib.parse import urlparse
                    parsed_base = urlparse(base_url)
                    href = f"{parsed_base.scheme}://{parsed_base.netloc}{href}"
                else:
                    # Relative path
                    if not base_url.endswith('/'):
                        base_url = base_url + '/'
                    href = base_url + href
            
            links.append({
                "url": href,
                "description": text[:200] if text else ""  # Limit description length
            })
        
        return links
    except Exception as e:
        logger.error(f"Error extracting links: {str(e)}")
        return []

def generate_content_hash(content):
    """Generate a hash for content"""
    return hashlib.md5(content.encode()).hexdigest()

def is_localhost_url(url):
    """Check if a URL is for localhost"""
    url_lower = url.lower()
    return 'localhost' in url_lower or '127.0.0.1' in url_lower 