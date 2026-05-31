import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RADAR_INDEX_FILE = DATA_DIR / "radar-index.json"

categories = [
    "Celulares",
    "Eletrodomésticos"
]

def generate_radar_index_data():
    index_data = {
        "last_updated": "2026-05-31T12:00:00Z",
        "indexes": []
    }
    for category in categories:
        score = random.randint(70, 99)
        change = round(random.uniform(-2.5, 2.5), 2)
        index_data["indexes"].append({
            "category": category,
            "score": score,
            "change": change,
            "status": "up" if change > 0 else ("down" if change < 0 else "stable")
        })
    return index_data

if __name__ == "__main__":
    data = generate_radar_index_data()
    with open(RADAR_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Dados do Radar Index™ gerados em {RADAR_INDEX_FILE}")
