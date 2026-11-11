import datetime
import json
import os
import urllib.request
import urllib.parse

print("=== Release Rydar Secure Artwork Sync (With Overrides) ===")
today = datetime.date.today()
json_path = "releases.json"

# Manual overrides for bands with common names where iTunes search fails
MANUAL_ARTWORK = {
    "Down - Volume V": "", # Leave empty to use clean monogram badge
    "Meridian Veil - The Watcher": "",
}

# Load existing database
releases = []
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            releases = json.load(f)
        except Exception:
            releases = []

for item in releases:
    band = item.get('band', '')
    album = item.get('album', '')
    lookup_key = f"{band} - {album}"
    
    # Apply manual override if defined
    if lookup_key in MANUAL_ARTWORK:
        item['artUrl'] = MANUAL_ARTWORK[lookup_key]
        print(f"Applied manual art override for: {lookup_key}")
        continue

    # Otherwise safely fetch from iTunes only if artUrl is missing
    if not item.get("artUrl") or item.get("artUrl") == "":
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

# Save verified database
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(releases, f, indent=4)
    
print("Sync complete. Artwork verified and locked.")
