import os
import json
from logger import logger

RAW_FILE = "data/raw_products.json"
DATABASE_FILE = "data/database/all_products.json"

def sync():
    if not os.path.exists(RAW_FILE):
        logger.warning("Arquivo raw_products.json não encontrado.")
        return

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        new_products = json.load(f)

    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    
    # No novo modelo, o fetch_products_realtime.py já filtrou por ID e Queda de Preço.
    # Portanto, o sync_database apenas atualiza o banco de dados principal.
    
    existing_products = []
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            existing_products = json.load(f)
            
    existing_dict = {p['id']: p for p in existing_products}
    
    for p in new_products:
        # Se for queda de preço, atualizamos o existente
        # Se for novo, adicionamos
        existing_dict[p['id']] = p
        
    final_list = list(existing_dict.values())
    
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Sincronização concluída: {len(new_products)} produtos processados.")
    logger.info(f"Total no banco de dados: {len(final_list)}")

if __name__ == "__main__":
    sync()
