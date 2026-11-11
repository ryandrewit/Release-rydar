import datetime
import json
import os
import urllib.request
import urllib.parse

print("=== Release Rydar Autonomous MusicBrainz & Art Sync ===")
today = datetime.date.today()
print(f"Running automated sync for: {today.strftime('%B %d, %Y')}")

json_path = "releases.json"

# Load existing releases
releases = []
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            releases = json.load(f)
        except Exception:
            releases = []

existing_bands = {item['band'].lower() for item in releases}

# 1. Query MusicBrainz API for recent heavy/metal releases
# MusicBrainz requires a descriptive User-Agent header per their terms of use
mb_url = "https://musicbrainz.org/ws/2/release/?query=tag:metal+AND+date:[2026-11-01 TO 2026-11-30]&fmt=json"

try:
    req = urllib.request.Request(mb_url, headers={'User-Agent': 'ReleaseRydar/1.0 (contact@releaserydar.com)'})
    with urllib.request.urlopen(req, timeout=10) as response:
        mb_data = json.loads(response.read().decode())
        releases_list = mb_data.get('releases', [])
        
        for rel in releases_list[:15]: # Grab top recent matches
            band_name = rel['artist-credit'][0]['name']
            album_title = rel['title']
            release_date = rel.get('date', str(today))
            
            # If band isn't already in our list, auto-discover and add them!
            if band_name.lower() not in existing_bands:
                new_item = {
                    "id": len(releases) + 1,
                    "band": band_name,
                    "album": album_title,
                    "genre": "Metal",
                    "type": "Album/Single",
                    "date": release_date,
                    "status": "recent",
                    "artUrl": "",
                    "artBg": "from-zinc-900 via-neutral-900 to-black",
                    "icon": "".join([c[0] for c in band_name.split()[:2]]).upper()
                }
                releases.insert(0, new_item)
                existing_bands.add(band_name.lower())
                print(f"Auto-discovered new release: {band_name} - {album_title}")
except Exception as e:
    print(f"Notice: MusicBrainz discovery skipped: {e}")

# 2. Automatically fetch official artwork for any items missing artUrl
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
    
print("releases.json successfully updated with auto-discovered releases and artwork!")
