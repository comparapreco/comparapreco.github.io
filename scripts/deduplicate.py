import json
import os
import unicodedata
from logger import logger

DATABASE_FILE = "data/database/all_products.json"

def normalize_text(text):
    if not text: return ""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return text.lower().strip()

def deduplicate():
    if not os.path.exists(DATABASE_FILE):
        return
    
    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    initial_count = len(products)
    unique_products = {}
    
    # Chave de deduplicação composta: Nome Normalizado + Preço
    # Isso evita que o mesmo produto com títulos levemente diferentes e mesmo preço polua a home
    for p in products:
        name_norm = normalize_text(p.get('name', ''))
        price = p.get('price', 0)
        
        # Pegamos apenas as primeiras 30 letras do nome para agrupar variações muito parecidas
        dedup_key = f"{name_norm[:30]}_{price}"
        
        if dedup_key not in unique_products:
            unique_products[dedup_key] = p
        else:
            # Se já existe, mantemos o que tiver o maior Quality Score
            if p.get('quality_score', 0) > unique_products[dedup_key].get('quality_score', 0):
                unique_products[dedup_key] = p

    final_list = list(unique_products.values())
    
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)
    
    removed = initial_count - len(final_list)
    logger.info(f"Deduplicação Inteligente: {removed} duplicados removidos. Total: {len(final_list)}")

if __name__ == "__main__":
    deduplicate()
