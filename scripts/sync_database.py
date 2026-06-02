import json
import os
from datetime import datetime
from logger import logger
import unicodedata
import re
from difflib import SequenceMatcher # Para similaridade de strings

def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text

SIMILARITY_THRESHOLD = 0.9 # 90% de similaridade para considerar duplicado por nome

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
                all_products = {p["id"]: p for p in data}
        except Exception as e:
            logger.error(f"Erro ao ler banco de dados: {e}")

    # Criar índices para busca rápida de duplicados
    existing_skus = {p.get('sku') for p in all_products.values() if p.get('sku')}
    existing_permalinks = {p.get('permalink') for p in all_products.values() if p.get('permalink')}
    existing_names_slugified = {slugify(p.get('name')) for p in all_products.values() if p.get('name')}

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
    duplicate_count = 0
    for p in new_offers:
        p_id = p["id"]
        p_sku = p.get('sku')
        p_permalink = p.get('permalink')
        p_name_slugified = slugify(p.get('name', ''))

        # Verificar duplicados antes de processar
        is_duplicate = False
        if p_id in all_products:
            is_duplicate = True
            logger.warning(f"Produto com ID {p_id} já existe no banco. Atualizando.")
        elif p_sku and p_sku in existing_skus:
            is_duplicate = True
            logger.warning(f"Produto com SKU {p_sku} já existe no banco. Ignorando novo.")
        elif p_permalink and p_permalink in existing_permalinks:
            is_duplicate = True
            logger.warning(f"Produto com permalink {p_permalink} já existe no banco. Ignorando novo.")
        else:
            # Verificar similaridade de nome para novos produtos
            for existing_slug in existing_names_slugified:
                if SequenceMatcher(None, p_name_slugified, existing_slug).ratio() >= SIMILARITY_THRESHOLD:
                    is_duplicate = True
                    logger.warning(f"Produto '{p.get('name')}' é muito similar a um existente. Ignorando novo.")
                    break
        
        if is_duplicate and p_id not in all_products: # Se for duplicado por SKU/Permalink/Nome e não por ID (que seria atualização)
            duplicate_count += 1
            continue # Pular este produto se for um duplicado real

        p["status"] = "active"
        p["last_seen"] = datetime.now().isoformat()
        
        if p_id in all_products:
            all_products[p_id].update(p)
            reactivated_count += 1
        else:
            all_products[p_id] = p
            new_count += 1

    logger.info(f"Sincronização concluída: {new_count} novos, {reactivated_count} atualizados, {duplicate_count} duplicados ignorados.")

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
