import os
import json
from typing import Any, Dict, List
from logger import logger

def fetch_all_products() -> List[Dict[str, Any]]:
    curated_path = "data/curated_products.json"
    if os.path.exists(curated_path):
        try:
            with open(curated_path, "r", encoding="utf-8") as f:
                products = [p for p in json.load(f) if p.get("name") and p.get("price") and p.get("price") > 0]
                logger.info(f"Sucesso: {len(products)} produtos carregados da lista curada.")
                return products
        except Exception as e:
            logger.error(f"Erro ao ler lista curada: {e}")
    return []

if __name__ == "__main__":
    products = fetch_all_products()
    os.makedirs("data", exist_ok=True)
    with open("data/raw_products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    logger.info("Resultados salvos em data/raw_products.json")
