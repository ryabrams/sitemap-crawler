import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime

# Configuration
INPUT_FILE = 'sitemaps.txt'
OUTPUT_DIR = 'CSVs'
DATE_STR = datetime.now().strftime('%Y-%m-%d')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'sitemap_urls_{DATE_STR}.csv')

def get_urls_from_sitemap(sitemap_url):
    """Fetches a sitemap and returns a list of URLs found within <loc> tags."""
    urls = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; SitemapScraper/1.0)'}
        response = requests.get(sitemap_url, headers=headers)
        response.raise_for_status()
        
        # Parse XML
        soup = BeautifulSoup(response.content, 'lxml-xml')
        
        # Find all <loc> tags
        loc_tags = soup.find_all('loc')
        for loc in loc_tags:
            urls.append(loc.text.strip())
            
        print(f"✅ Successfully extracted {len(urls)} URLs from {sitemap_url}")
        
    except Exception as e:
        print(f"❌ Error scraping {sitemap_url}: {e}")
        
    return urls

def main():
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    all_urls = []

    # Read sitemaps from file
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, 'r') as f:
        sitemaps = [line.strip() for line in f if line.strip()]

    print(f"Starting scrape for {len(sitemaps)} sitemaps...")

    # Scrape each sitemap
    for sitemap in sitemaps:
        urls = get_urls_from_sitemap(sitemap)
        # Add source sitemap for reference in the CSV
        for url in urls:
            all_urls.append({'source_sitemap': sitemap, 'url': url})

    # Write to CSV
    if all_urls:
        keys = ['source_sitemap', 'url']
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as output_csv:
            dict_writer = csv.DictWriter(output_csv, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_urls)
        print(f"🎉 Success! Saved {len(all_urls)} URLs to {OUTPUT_FILE}")
    else:
        print("⚠️ No URLs found to write.")

if __name__ == "__main__":
    main()