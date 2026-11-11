import datetime
import json
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

print("=== Release Rydar Autonomous Feed Scraper ===")
today = datetime.date.today()
print(f"Running automated discovery for: {today.strftime('%B %d, %Y')}")

json_path = "releases.json"

# Load existing releases or start fresh
releases = []
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            releases = json.load(f)
        except Exception:
            releases = []

# Example: Pulling from heavy music RSS / release feeds to auto-discover drops
# You can add more trusted RSS feeds here (e.g., metal release trackers)
rss_feeds = [
    # Example RSS feed URL for metal/rock releases
    # "https://www.theprp.com/feed/",
]

# For now, let's also ensure our iTunes metadata lookup is robust for any auto-discovered or existing items
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
                        print(f"Auto-fetched artwork for: {search_term}")
        except Exception as e:
            print(f"Notice: Could not fetch art for {search_term}: {e}")

# Save back to repository
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(releases, f, indent=4)
    
print("releases.json successfully synced and updated!")
