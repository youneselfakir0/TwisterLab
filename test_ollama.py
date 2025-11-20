import json

import httpx

urls = ["http://ollama:11434/api/tags", "http://edgeserver:11434/api/tags"]
for url in urls:
    try:
        r = httpx.get(url, timeout=5)
        print(f"{url}: OK {r.status_code}")
        data = r.json()
        models = [m["name"] for m in data.get("models", [])]
        print(f"  Models: {models}")
    except Exception as e:
        print(f"{url}: ERROR - {e}")
