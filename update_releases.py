import datetime
import json
import os
import urllib.request
import urllib.parse

print("=== Release Rydar Monthly Pruning & Sync ===")
today = datetime.date.today()
json_path = "releases.json"

# Manual artwork overrides for tricky common band names
MANUAL_ARTWORK = {
    "Down - Volume V": "",
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

# --- CALENDAR-MONTH PRUNING LOGIC ---
# Keep only releases from the current calendar month onward.
# As soon as a new month starts, previous months are automatically wiped out.
current_year_month = (today.year, today.month)

fresh_releases = []
for item in releases:
    try:
        release_date = datetime.date.fromisoformat(item['date'])
        release_year_month = (release_date.year, release_date.month)
        
        # Keep if release is in the current month or a future month
        if release_year_month >= current_year_month:
            fresh_releases.append(item)
        else:
            print(f"Pruned past month release: {item['band']} - {item['album']} ({item['date']})")
    except Exception as e:
        print(f"Skipping malformed date item: {item.get('band')} - {e}")

releases = fresh_releases

# --- ARTWORK ENRICHMENT ---
for item in releases:
    band = item.get('band', '')
    album = item.get('album', '')
    lookup_key = f"{band} - {album}"
    
    if lookup_key in MANUAL_ARTWORK:
        item['artUrl'] = MANUAL_ARTWORK[lookup_key]
        continue

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

# Save the clean database back to the repo
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(releases, f, indent=4)
    
print(f"Sync complete. Active database items for current/future months: {len(releases)}")
