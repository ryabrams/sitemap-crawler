import cloudscraper
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import time

# Configuration
INPUT_FILE = 'sitemaps.txt'
OUTPUT_DIR = 'CSVs'
DATE_STR = datetime.now().strftime('%Y-%m-%d')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'sitemap_urls_{DATE_STR}.csv')

def get_urls_from_sitemap(sitemap_url):
    urls = []
    
    # Create a CloudScraper instance to bypass WAF/Cloudflare
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    print(f"--- Processing: {sitemap_url} ---")
    
    try:
        # We use scraper.get() instead of requests.get()
        response = scraper.get(sitemap_url)
        
        if response.status_code != 200:
            print(f"❌ Blocked or Failed: Status {response.status_code}")
            # Print a snippet of the response to see if it's a specific error page
            print(f"Response snippet: {response.text[:200]}")
            return []

        # Parse content
        # We use 'lxml' which is robust for XML parsing
        soup = BeautifulSoup(response.content, 'lxml-xml')
        
        # Method 1: Standard <loc> tags
        loc_tags = soup.find_all('loc')
        
        for loc in loc_tags:
            url_text = loc.text.strip()
            if url_text:
                urls.append(url_text)
                
        print(f"✅ Extracted {len(urls)} URLs")

    except Exception as e:
        print(f"❌ Error: {e}")
        
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

    print(f"🚀 Starting scrape for {len(sitemaps)} sitemaps using CloudScraper...")

    for sitemap in sitemaps:
        urls = get_urls_from_sitemap(sitemap)
        for url in urls:
            all_data.append({'source_sitemap': sitemap, 'url': url})
        
        # Polite delay
        time.sleep(2)

    if all_data:
        keys = ['source_sitemap', 'url']
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as output_csv:
            dict_writer = csv.DictWriter(output_csv, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_data)
        print(f"🎉 Success! File created at: {OUTPUT_FILE}")
    else:
        print("⚠️ No URLs extracted. The firewall might still be blocking GitHub IPs.")

if __name__ == "__main__":
    main()
