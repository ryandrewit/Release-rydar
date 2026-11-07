import datetime
import json
import os
import urllib.request
import xml.etree.ElementTree as ET

print("=== Release Rydar Automated Feed Scraper ===")
today = datetime.date.today()
print(f"Running automated scrape for: {today.strftime('%B %d, %Y')}")

json_path = "releases.json"

# Load existing releases if file exists, or start fresh
releases = []
if os.path.exists(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            releases = json.load(f)
    except Exception as e:
        print(f"Error loading existing JSON: {e}")

# Fetch live metal news / release RSS feed
feed_url = "https://metalinjection.net/feed"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    req = urllib.request.Request(feed_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        xml_data = response.read()
        
        # Parse XML feed using standard library
        root = ET.fromstring(xml_data)
        channel = root.find('channel')
        
        fetched_count = 0
        for item in channel.findall('item'):
            title = item.find('title')
            pub_date = item.find('pubDate')
            
            if title is not None and title.text:
                text = title.text
                # Look for album/release indicators in headlines
                if any(keyword in text.lower() for keyword in ['album', 'stream', 'premiere', 'ep', 'announce new', 'releases']):
                    # Clean up title to extract band / album info
                    clean_title = text.split('|')[0].split('-')[0].strip()
                    
                    # Prevent duplicates
                    if not any(r['album'] == clean_title for r in releases):
                        new_release = {
                            "id": len(releases) + 1,
                            "band": "Featured Artist",
                            "album": clean_title,
                            "genre": "Metal",
                            "type": "Album",
                            "date": today.isoformat(),
                            "status": "recent",
                            "artUrl": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600&auto=format&fit=crop&q=80",
                            "artBg": "from-zinc-900 to-zinc-950"
                        }
                        releases.insert(0, new_release)
                        fetched_count += 1

        print(f"Successfully scraped and added {fetched_count} new entries from live feeds.")

except Exception as e:
    print(f"Network error while fetching feed (keeping existing data): {e}")

# Save updated list back to releases.json
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(releases, f, indent=4)

print("releases.json successfully updated and saved!")
