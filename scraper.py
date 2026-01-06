import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import time
import gzip
import io

# Configuration
INPUT_FILE = 'sitemaps.txt'
OUTPUT_DIR = 'CSVs'
DATE_STR = datetime.now().strftime('%Y-%m-%d')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'sitemap_urls_{DATE_STR}.csv')

def get_sitemap_content(url):
    """Fetches sitemap content, handling both plain text and GZIP compression."""
    # Mimic a real browser to avoid 403 Forbidden blocks
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    # Check if the content is gzipped (by extension or header)
    if url.endswith('.gz') or response.headers.get('Content-Type') == 'application/x-gzip':
        try {
            # Decompress gzip content
            buf = io.BytesIO(response.content)
            f = gzip.GzipFile(fileobj=buf)
            content = f.read()
            return content
        } except OSError {
            # Fallback if it looked like gzip but wasn't
            return response.content
        }
            
    return response.content

def get_urls_from_sitemap(sitemap_url):
    """Parses XML content to extract URLs."""
    urls = []
    try {
        content = get_sitemap_content(sitemap_url)
        
        # Parse XML (lxml is faster, but html.parser is more forgiving of errors)
        soup = BeautifulSoup(content, 'lxml-xml')
        
        # Find all <loc> tags
        loc_tags = soup.find_all('loc')
        for loc in loc_tags:
            text = loc.text.strip()
            # Basic filter to ensure we aren't capturing empty tags
            if text:
                urls.append(text)
            
        print(f"✅ Extracted {len(urls)} URLs from {sitemap_url}")
        
    } catch (Exception e) {
        print(f"❌ Error scraping {sitemap_url}: {e}")
        
    return urls

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    all_data = []

    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, 'r') as f:
        sitemaps = [line.strip() for line in f if line.strip()]

    print(f"Starting scrape for {len(sitemaps)} sitemaps...")

    for sitemap in sitemaps:
        urls = get_urls_from_sitemap(sitemap)
        for url in urls:
            all_data.append({'source_sitemap': sitemap, 'url': url})
        
        # Polite delay to prevent rate limiting
        time.sleep(1)

    if all_data:
        keys = ['source_sitemap', 'url']
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as output_csv:
            dict_writer = csv.DictWriter(output_csv, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_data)
        print(f"🎉 Success! Saved {len(all_data)} URLs to {OUTPUT_FILE}")
    else:
        print("⚠️ No URLs found. Please check your sitemap links.")

if __name__ == "__main__":
    main()