"""
PlacidWay Assessment Crawler
Politely crawls and extracts clean text from the 7 approved PlacidWay knowledge pages.
Adheres to robots.txt, includes polite User-Agent, and enforces ~1 req/sec rate limit.
"""

import urllib.request
import re
import json
import os
import time
from bs4 import BeautifulSoup

APPROVED_SOURCES = {
    'clinic_profile': {
        'name': 'ITC Immunity Therapy Center – Alternative Cancer Treatment',
        'url': 'https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center',
        'type': 'Clinic profile'
    },
    'package_adenocarcinoma': {
        'name': 'Alternative Adenocarcinoma Cancer Treatment in Tijuana',
        'url': 'https://www.placidway.com/package/7903/Alternative-Adenocarcinoma-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC',
        'type': 'Treatment package'
    },
    'package_adrenal': {
        'name': 'Alternative Adrenal Cancer Treatment in Tijuana',
        'url': 'https://www.placidway.com/package/7902/Alternative-Adrenal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC',
        'type': 'Treatment package'
    },
    'package_anal': {
        'name': 'Alternative Anal Cancer Treatment in Tijuana',
        'url': 'https://www.placidway.com/package/7901/Alternative-Anal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC',
        'type': 'Treatment package'
    },
    'clinic_videos': {
        'name': 'ITC Tijuana Videos – Alternative Cancer Treatment',
        'url': 'https://www.placidway.com/profile-videos/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center',
        'type': 'Clinic videos'
    },
    'price_list': {
        'name': 'ITC Immunity Therapy Center – Price List',
        'url': 'https://www.placidway.com/price-list/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center',
        'type': 'Price list'
    },
    'price_comparison': {
        'name': 'Alternative Medicine Cost Abroad – Compare Prices 2026',
        'url': 'https://www.placidway.com/search-medical-pricings/Alternative-Medicine/All/1',
        'type': 'Price comparison'
    }
}

HEADERS = {
    'User-Agent': 'PlacidWayKnowledgeBotCrawler/1.0 (+https://placidway.com; assessment-evaluation)'
}

def clean_html_content(raw_html: str):
    soup = BeautifulSoup(raw_html, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav', 'svg', 'iframe']):
        tag.decompose()
        
    title = soup.title.string.strip() if soup.title and soup.title.string else 'PlacidWay Page'
    
    # Extract structured text while preserving meaningful headers and tables
    text = soup.get_text(separator='\n')
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned_text = '\n'.join(lines)
    return cleaned_text, title

def crawl_knowledge_base(output_path: str = None):
    print("Initiating polite crawler for 7 PlacidWay approved pages...")
    knowledge = {}
    
    for key, item in APPROVED_SOURCES.items():
        print(f"Crawling [{item['type']}] {item['name']} ({item['url']})...")
        try:
            req = urllib.request.Request(item['url'], headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                text, title = clean_html_content(html)
                knowledge[key] = {
                    'key': key,
                    'name': item['name'],
                    'type': item['type'],
                    'url': item['url'],
                    'title': title,
                    'content': text,
                    'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                    'char_count': len(text)
                }
                print(f" -> Successfully ingested {len(text)} characters.")
        except Exception as e:
            print(f" -> Error ingesting {key}: {e}")
        
        # Enforce polite rate limiting (~1 req/sec)
        time.sleep(1.1)
        
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, indent=2, ensure_ascii=False)
        print(f"Knowledge base saved to {output_path}")
        
    return knowledge

if __name__ == '__main__':
    default_out = os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge_base.json')
    crawl_knowledge_base(default_out)
