import os
import json
import requests
import time
import random
from datetime import datetime
from typing import Any, Dict, List
from logger import logger

HISTORY_FILE = "data/published_history.json"
RAW_DATA_FILE = "data/raw_products.json"
BLACKLIST_FILE = "data/blacklist_ids.json"

def load_json(filepath, default):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_from_api(category_id: str, category_name: str) -> List[Dict[str, Any]]:
    url = f"https://api.mercadolibre.com/sites/MLB/search?category={category_id}&sort=relevance&limit=50"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            results = response.json().get("results", [])
            products = []
            for r in results:
                price = r.get("price", 0)
                old_price = r.get("original_price") or price * 1.2
                products.append({
                    "id": r.get("id"),
                    "name": r.get("title"),
                    "price": price,
                    "original_price": old_price,
                    "permalink": r.get("permalink"),
                    "thumbnail": r.get("thumbnail"),
                    "image": r.get("thumbnail", "").replace("-I.jpg", "-O.jpg"),
                    "custom_category_slug": category_name,
                    "custom_discount_pct": int(((old_price - price) / old_price) * 100) if old_price > price else 0,
                    "status": "active",
                    "data_coleta": datetime.now().isoformat()
                })
            return products
    except: pass
    return []

def main():
    categories = {"celulares": "MLB1051", "informatica": "MLB1648", "eletrodomesticos": "MLB5726", "games": "MLB1144", "tv-e-video": "MLB1000", "casa": "MLB1574", "beleza": "MLB1246", "ferramentas": "MLB1501", "moveis": "MLB1574"}
    
    history = load_json(HISTORY_FILE, {"published_ids": [], "price_history": {}})
    blacklist = set(load_json(BLACKLIST_FILE, []))
    published_ids = set(history.get("published_ids", []))
    price_history = history.get("price_history", {})
    
    all_found = []
    for name, ml_id in categories.items():
        products = fetch_from_api(ml_id, name)
        for p in products:
            p_id = p["id"]
            # BLOQUEIO POR ID OU TERMO
            if p_id in blacklist or any(term in p["name"].lower() for term in ["whey", "dark lab"]):
                continue
                
            if p_id in published_ids:
                old_price = price_history.get(p_id, p["price"])
                if p["price"] < old_price * 0.95:
                    p["is_price_drop"] = True
                    p["old_price_recorded"] = old_price
                    all_found.append(p)
                    price_history[p_id] = p["price"]
            else:
                all_found.append(p)
                price_history[p_id] = p["price"]
                history["published_ids"].append(p_id)
    
    save_json(RAW_DATA_FILE, all_found)
    history["price_history"] = price_history
    save_json(HISTORY_FILE, history)
    logger.info(f"Busca finalizada. {len(all_found)} produtos válidos encontrados.")

if __name__ == "__main__":
    main()
