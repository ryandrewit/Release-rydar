import datetime
import json
import os
import urllib.request
import urllib.parse

print("=== Release Rydar Automated Art & Feed Sync ===")
today = datetime.date.today()
print(f"Running automated sync for: {today.strftime('%B %d, %Y')}")

json_path = "releases.json"

if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        releases = json.load(f)
    
    # Automatically query official music metadata API for each release's artwork
    for item in releases:
        # Only fetch if artUrl is currently empty
        if not item.get("artUrl"):
            search_term = f"{item['band']} {item['album']}"
            api_url = f"https://itunes.apple.com/search?term={urllib.parse.quote(search_term)}&entity=album&limit=1"
            
            try:
                req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    if data['resultCount'] > 0:
                        result = data['results'][0]
                        if 'artworkUrl100' in result:
                            # Upgrade standard thumbnail to high-res 600x600 official cover art
                            item['artUrl'] = result['artworkUrl100'].replace('100x100bb.jpg', '600x600bb.jpg')
                            print(f"Fetched official artwork for: {search_term}")
            except Exception as e:
                print(f"Notice: Could not fetch art for {search_term}: {e}")

    # Save updated JSON back to repository
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(releases, f, indent=4)
        
    print("releases.json successfully updated with live artwork!")
else:
    print("releases.json not found.")
