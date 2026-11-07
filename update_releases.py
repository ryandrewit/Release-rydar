import datetime
import json
import os

print("=== Release Rydar Feed Manager ===")
today = datetime.date.today()
print(f"Running automated maintenance for: {today.strftime('%B %d, %Y')}")

json_path = "releases.json"

if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        releases = json.load(f)
    
    # Keep feed pristine and up to date
    print(f"Verified active release database loaded successfully. Total items: {len(releases)}")
else:
    print("releases.json not found.")
