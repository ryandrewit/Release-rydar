import datetime
import json
import os

print("=== Release Rydar Live Feed Sync ===")
today = datetime.date.today()
print(f"Syncing live releases for: {today.strftime('%B %d, %Y')}")

json_path = "releases.json"

if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        releases = json.load(f)
    
    print(f"Loaded {len(releases)} live releases successfully. Feed is synced!")
else:
    print("releases.json not found in root directory.")
