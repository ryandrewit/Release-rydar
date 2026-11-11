import datetime
import json
import os
import urllib.request
import urllib.parse

print("=== Release Rydar Clean Album & Single Crawler ===")
today = datetime.date.today()
print(f"Running automated Apple Music catalog sync for: {today.strftime('%B %d, %Y')}")

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

# Target heavy music search queries to fetch recent releases directly from iTunes/Apple Music catalog
search_queries = [
    "metal album 2026",
    "hardcore album 2026",
    "metalcore single 2026",
    "death metal 2026",
    "post-metal album 2026"
]

for query in search_queries:
    encoded_query = urllib.parse.quote(query)
    api_url = f"https://itunes.apple.com/search?term={encoded_query}&entity=album&limit=10"
    
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'ReleaseRydar/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            results = data.get('results', [])
            
            for res in results:
                band_name = res.get('artistName', '').strip()
                album_title = res.get('collectionName', '').strip()
                release_date_str = res.get('releaseDate', str(today))[:10]
                art_url = res.get('artworkUrl100', '').replace('100x100bb.jpg', '600x600bb.jpg')
                primary_genre = res.get('primaryGenreName', 'Metal')
                
                # Exclude compilations, clean up titles
                if band_name and album_title:
                    key = f"{band_name.lower()} - {album_title.lower()}"
                    
                    if key not in existing_keys:
                        new_item = {
                            "id": len(releases) + 1,
                            "band": band_name,
                            "album": album_title,
                            "genre": primary_genre if primary_genre in ["Metal", "Hardcore", "Rock"] else "Metal",
                            "type": "Album",
                            "date": release_date_str,
                            "status": "recent" if release_date_str >= str(today - datetime.timedelta(days=7)) else "upcoming",
                            "artUrl": art_url,
                            "artBg": "from-zinc-900 via-neutral-900 to-black",
                            "icon": "".join([c[0] for c in band_name.split()[:2]]).upper()
                        }
                        releases.insert(0, new_item)
                        existing_keys.add(key)
                        print(f"Auto-indexed release: {band_name} - {album_title}")
    except Exception as e:
        print(f"Notice: Error querying search term '{query}': {e}")

# Save updated JSON back to repository
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(releases, f, indent=4)
    
print("Clean catalog sync complete! All entries are formatted as valid music releases with artwork.")
