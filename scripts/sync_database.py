import json
import os
from datetime import datetime
from logger import logger

DB_PATH = "data/database/all_products.json"
NEW_OFFERS_PATH = "data/new_offers.json"

def sync_db():
    logger.info("Sincronizando banco de dados de produtos permanentes...")
    
    # Carregar banco atual
    all_products = {}
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Usar ID como chave para busca rápida
                all_products = {p['id']: p for p in data}
        except Exception as e:
            logger.error(f"Erro ao ler banco de dados: {e}")

    # Carregar novas ofertas
    new_offers = []
    if os.path.exists(NEW_OFFERS_PATH):
        try:
            with open(NEW_OFFERS_PATH, "r", encoding="utf-8") as f:
                new_offers = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler novas ofertas: {e}")

    # Marcar todos como 'expirado' inicialmente (serão reativados se estiverem nas novas ofertas)
    # Mas apenas se já existirem no banco. Novos produtos entram como 'ativo'.
    for p_id in all_products:
        all_products[p_id]['status'] = 'expired'

    # Atualizar ou adicionar novos
    new_count = 0
    reactivated_count = 0
    for p in new_offers:
        p_id = p['id']
        p['status'] = 'active'
        p['last_seen'] = datetime.now().isoformat()
        
        if p_id in all_products:
            all_products[p_id].update(p)
            reactivated_count += 1
        else:
            all_products[p_id] = p
            new_count += 1

    # Salvar banco atualizado
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(list(all_products.values()), f, ensure_ascii=False, indent=2)
        
        active = sum(1 for p in all_products.values() if p.get('status') == 'active')
        expired = sum(1 for p in all_products.values() if p.get('status') == 'expired')
        
        logger.info(f"Sincronização concluída: {new_count} novos, {reactivated_count} atualizados.")
        logger.info(f"Total no Banco: {len(all_products)} ({active} ativos, {expired} expirados)")
    except Exception as e:
        logger.error(f"Erro ao salvar banco de dados: {e}")

if __name__ == "__main__":
    sync_db()
