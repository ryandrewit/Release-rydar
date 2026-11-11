import datetime
import json
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re

print("=== Release Rydar Autonomous Heavy Music Crawler ===")
today = datetime.date.today()
print(f"Running automated scan for: {today.strftime('%B %d, %Y')}")

json_path = "releases.json"

# Load existing releases
releases = []
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            releases = json.load(f)
        except Exception:
            releases = []

existing_keys = {f"{item['band'].lower()} - {item['album'].lower()}" for item in releases}

# Multi-channel heavy music feeds for real-time single and album discovery
rss_sources = [
    "https://www.theprp.com/feed/",
    "https://blabbermouth.net/feed",
    "https://www.kerrang.com/rss.xml"
]

for feed_url in rss_sources:
    try:
        req = urllib.request.Request(feed_url, headers={'User-Agent': 'ReleaseRydarBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # Parse RSS feed items
            for item in root.findall('.//item'):
                title = item.find('title')
                if title is not None and title.text:
                    text = title.text.strip()
                    
                    # Target keywords for single/album releases and announcements
                    lower_text = text.lower()
                    if any(kw in lower_text for kw in ["release", "single", "album", "announce", "premiere", "stream", "track"]):
                        # Clean up common prefixes like "Review:", "News:", etc.
                        cleaned_text = re.sub(r'^(News|Review|Premiere|Stream):\s*', '', text, flags=re.IGNORECASE)
                        
                        # Split by typical separators (dash, colon, em-dash)
                        parts = re.split(r'[-–—:]', cleaned_text)
                        if len(parts) >= 2:
                            band_name = parts[0].strip()
                            # Clean up trailing parentheses or extra promotional taglines
                            album_title = parts[1].strip().split('(')[0].split('"')[1] if '"' in parts[1] else parts[1].strip().split('(')[0].strip()
                            
                            key = f"{band_name.lower()} - {album_title.lower()}"
                            if key not in existing_keys and len(band_name) > 1 and len(album_title) > 1:
                                new_item = {
                                    "id": len(releases) + 1,
                                    "band": band_name,
                                    "album": album_title,
                                    "genre": "Metal / Hardcore",
                                    "type": "Single/Album",
                                    "date": str(today),
                                    "status": "recent",
                                    "artUrl": "",
                                    "artBg": "from-zinc-900 via-neutral-900 to-black",
                                    "icon": "".join([c[0] for c in band_name.split()[:2]]).upper()
                                }
                                releases.insert(0, new_item)
                                existing_keys.add(key)
                                print(f"Auto-captured new drop: {band_name} - {album_title}")
    except Exception as e:
        print(f"Notice: Error parsing feed {feed_url}: {e}")

# Automatically fetch official high-res artwork for any items missing artUrl
for item in releases:
    if not item.get("artUrl") or item.get("artUrl") == "":
        search_term = f"{item['band']} {item['album']}"
        api_url = f"https://itunes.apple.com/search?term={urllib.parse.quote(search_term)}&entity=album&limit=1"
        
        try:
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data['resultCount'] > 0:
                    result = data['results'][0]
                    if 'artworkUrl100' in result:
                        item['artUrl'] = result['artworkUrl100'].replace('100x100bb.jpg', '600x600bb.jpg')
                        print(f"Fetched official artwork for: {search_term}")
        except Exception as e:
            print(f"Notice: Could not fetch art for {search_term}: {e}")

# Save updated JSON back to repository
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(releases, f, indent=4)
    
print("Autonomous crawler sync completed successfully!")
