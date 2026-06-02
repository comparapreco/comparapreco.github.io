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

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"published_ids": [], "price_history": {}}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def fetch_from_api(category_id: str, category_name: str) -> List[Dict[str, Any]]:
    """Busca produtos via API do Mercado Livre."""
    url = f"https://api.mercadolibre.com/sites/MLB/search?category={category_id}&sort=relevance&limit=50"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
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
    except Exception as e:
        logger.error(f"Erro ao buscar categoria {category_name}: {e}")
    return []

def main():
    categories = {
        "celulares": "MLB1051",
        "informatica": "MLB1648",
        "eletrodomesticos": "MLB5726",
        "games": "MLB1144",
        "tv-e-video": "MLB1000",
        "casa": "MLB1574",
        "beleza": "MLB1246",
        "ferramentas": "MLB1501",
        "moveis": "MLB1574"
    }
    
    history = load_history()
    published_ids = set(history.get("published_ids", []))
    price_history = history.get("price_history", {})
    
    all_found = []
    new_count = 0
    duplicate_count = 0
    price_drop_count = 0
    
    for name, ml_id in categories.items():
        logger.info(f"Iniciando busca em tempo real para: {name}")
        products = fetch_from_api(ml_id, name)
        
        for p in products:
            p_id = p["id"]
            current_price = p["price"]
            
            # Verifica se já foi publicado
            if p_id in published_ids:
                duplicate_count += 1
                # Verifica queda de preço significativa (> 5%)
                old_price = price_history.get(p_id, current_price)
                if current_price < old_price * 0.95:
                    logger.info(f"🔥 QUEDA DE PREÇO detectada: {p['name']} ({old_price} -> {current_price})")
                    p["is_price_drop"] = True
                    p["old_price_recorded"] = old_price
                    all_found.append(p)
                    price_drop_count += 1
                    price_history[p_id] = current_price # Atualiza para o novo preço baixo
            else:
                # Produto novo
                new_count += 1
                all_found.append(p)
                price_history[p_id] = current_price
        
        time.sleep(1)

    # Salva os produtos encontrados para o próximo passo do pipeline
    with open(RAW_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_found, f, ensure_ascii=False, indent=2)
    
    # Atualiza o histórico (apenas IDs que serão processados agora)
    # Nota: No pipeline real, os IDs só devem ir para published_ids após o commit bem sucedido.
    # Mas para este script, vamos registrar que os encontramos.
    for p in all_found:
        if p["id"] not in published_ids:
            history["published_ids"].append(p["id"])
    
    history["price_history"] = price_history
    save_history(history)
    
    logger.info(f"--- RELATÓRIO DE BUSCA ---")
    logger.info(f"Produtos novos encontrados: {new_count}")
    logger.info(f"Produtos descartados (duplicados): {duplicate_count}")
    logger.info(f"Produtos com queda de preço: {price_drop_count}")
    logger.info(f"Total para processamento: {len(all_found)}")

if __name__ == "__main__":
    main()
