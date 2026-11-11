import datetime
import json
import os
import urllib.request
import urllib.parse

print("=== Release Rydar Secure Artwork Sync ===")
today = datetime.date.today()
json_path = "releases.json"

# Load existing database
releases = []
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            releases = json.load(f)
        except Exception:
            releases = []

# ONLY enrich artwork for items already explicitly defined in releases.json.
# This script will NEVER auto-discover or add unverified bands.
for item in releases:
    if not item.get("artUrl") or item.get("artUrl") == "":
        band = item.get('band', '')
        album = item.get('album', '')
        search_term = f"{band} {album}"
        
        api_url = f"https://itunes.apple.com/search?term={urllib.parse.quote(search_term)}&entity=album&limit=1"
        
        try:
            req = urllib.request.Request(api_url, headers={'User-Agent': 'ReleaseRydar/1.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data.get('resultCount', 0) > 0:
                    result = data['results'][0]
                    if 'artworkUrl100' in result:
                        item['artUrl'] = result['artworkUrl100'].replace('100x100bb.jpg', '600x600bb.jpg')
                        print(f"Synced artwork for: {search_term}")
        except Exception as e:
            print(f"Notice: Art lookup skipped for {search_term}: {e}")

# Save the pristine, locked-down database back to repository
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(releases, f, indent=4)
    
print("Sync complete. Database locked to curated entries only.")
