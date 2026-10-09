import os
import json
import httpx
from datetime import date

# 1. Сразу проверяем ключ
key = os.environ.get("YANDEX_API_KEY")
if not key:
    print("❌ ERROR: YANDEX_API_KEY не найден в переменных окружения!")
    raise RuntimeError("Missing API key")
else:
    # Не показываем весь ключ, но покажем, что он есть
    print(f"✅ DEBUG: API key found (length {len(key)})")

base = "https://api.rasp.yandex-net.ru/v3.0"
today = date.today().isoformat()

stations = {
    "s2000003": "Москва (Курский вокзал)",
    "s9603206": "Санкт-Петербург (Московский вокзал)",
    "s2210001": "Симферополь (Пассажирский)",
}

result = {}

for code, name in stations.items():
    print(f"🔍 DEBUG: запрашиваем станцию {code} ({name})")
    try:
        resp = httpx.get(
            f"{base}/schedule/",
            params={
                "apikey": key,
                "station": code,
                "transport_types": "train",
                "event": "arrival",
                "date": today,
                "lang": "ru_RU",
                "format": "json",
            },
            timeout=10.0
        )
        # Если Яндекс сказал «нет» (403, 404 и т.д.) — тут будет понятная ошибка
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"❌ ERROR: запрос к станции {code} упал: {e}")
        raise e

    trains = []
    schedule = data.get("schedule", [])
    if not isinstance(schedule, list):
        print(f"⚠️ WARNING: schedule не список для {code}, тип: {type(schedule)}")
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
    print(f"✅ DEBUG: станция {code} -> {len(trains)} поездов")

# Пишем файл в корень репозитория
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ DEBUG: data.json успешно записан!")
