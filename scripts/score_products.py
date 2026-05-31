import os
import json
from logger import logger

def process(input_p, output_p):
    if not os.path.exists(input_p):
        products = []
    else:
        with open(input_p, "r", encoding="utf-8") as f:
            try:
                raw_data = json.load(f)
                products = []
                seen_ids = set()
                # Categorias permitidas
                ALLOWED_CATEGORIES = ["celulares", "eletrodomesticos"]
                
                for p in raw_data:
                    p_id = p.get("id")
                    cat = p.get("custom_category_slug")
                    if p_id and p_id not in seen_ids and p.get("name") and p.get("price", 0) > 0:
                        if cat in ALLOWED_CATEGORIES:
                            products.append(p)
                            seen_ids.add(p_id)
            except Exception as e:
                logger.error(f"Erro ao ler {input_p}: {e}")
                products = []
    
    os.makedirs(os.path.dirname(output_p), exist_ok=True)
    with open(output_p, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    logger.info(f"Scoring concluído: {len(products)} produtos das categorias permitidas processados.")

if __name__ == "__main__":
    process("data/raw_products.json", "data/scored_products.json")
