import json
import os
from datetime import datetime
from logger import logger

DB_PATH = "data/database/all_products.json"
NEW_OFFERS_PATH = "data/scored_products.json" # Usar o arquivo já filtrado pelo score_products

def sync_db():
    logger.info("Sincronizando banco de dados com filtro de categorias (Celulares e Eletrodomésticos)...")
    
    # Carregar novas ofertas (já filtradas no score_products.py)
    new_offers = []
    if os.path.exists(NEW_OFFERS_PATH):
        try:
            with open(NEW_OFFERS_PATH, "r", encoding="utf-8") as f:
                new_offers = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler novas ofertas: {e}")

    # O banco de dados final será APENAS o que passou no filtro
    all_products = []
    for p in new_offers:
        p['status'] = 'active'
        p['last_seen'] = datetime.now().isoformat()
        all_products.append(p)

    # Salvar banco limpo
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)
        logger.info(f"Sincronização concluída: {len(all_products)} produtos ativos no nicho escolhido.")
    except Exception as e:
        logger.error(f"Erro ao salvar banco de dados: {e}")

if __name__ == "__main__":
    sync_db()
