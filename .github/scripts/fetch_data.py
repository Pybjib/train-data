import os
import json
import httpx
from datetime import date

key = os.environ.get("YANDEX_API_KEY")
if not key:
    print("ERROR: YANDEX_API_KEY not found!")
    raise RuntimeError("Missing API key")

base = "https://api.rasp.yandex-net.ru/v3.0"
today = date.today().isoformat()

stations = {
    "s2000003": "Москва (Курский вокзал)",
    "s9603206": "Санкт-Петербург (Московский вокзал)",
    "s2018100": "Симферополь (Пассажирский)",
}

result = {}

for code, name in stations.items():
    print(f"DEBUG: fetching station {code} ({name})")
    resp = httpx.get(f"{base}/schedule/", params={
        "apikey": key,
        "station": code,
        "transport_types": "train",
        "event": "arrival",
        "date": today,
        "lang": "ru_RU",
        "format": "json",
    }, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()

    trains = []
    schedule = data.get("schedule", [])
    if not isinstance(schedule, list):
        schedule = []

    for item in schedule:
        trains.append({
            "number": item["thread"]["number"],
            "title": item["thread"]["title"],
            "arrival": item.get("arrival", ""),
            "platform": item.get("platform", ""),
        })
    trains.sort(key=lambda t: t["arrival"])
    result[code] = trains
    print(f"DEBUG: station {code} -> {len(trains)} trains")

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("DEBUG: data.json written successfully")
