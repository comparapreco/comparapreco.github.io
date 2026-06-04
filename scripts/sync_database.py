"""
sync_database.py
Sincroniza os produtos aprovados (affiliate_products.json) com o banco
principal (all_products.json), mantendo um histórico rotativo de até 500
produtos e garantindo que o banco nunca fique vazio.
"""

import os
import json
from datetime import datetime, timedelta

try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

# Prioridade de entrada: affiliate > scored > raw
INPUT_FILES = [
    "data/affiliate_products.json",
    "data/scored_products.json",
    "data/raw_products.json",
]
DATABASE_FILE = "data/database/all_products.json"
MAX_DB_SIZE = 500          # Máximo de produtos no banco
MAX_AGE_DAYS = 30          # Remover produtos com mais de 30 dias sem atualização


def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def sync():
    # Carregar novos produtos (usar o arquivo mais completo disponível)
    new_products = []
    source_used = None
    for input_file in INPUT_FILES:
        data = load_json(input_file, [])
        if data:
            new_products = data
            source_used = input_file
            break

    if not new_products:
        logger.warning("Nenhum produto novo encontrado em nenhum arquivo de entrada.")
        return

    logger.info(f"Carregando {len(new_products)} produtos de: {source_used}")

    # Carregar banco existente
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    existing_products = load_json(DATABASE_FILE, [])
    existing_dict = {p["id"]: p for p in existing_products if "id" in p}

    # Adicionar/atualizar produtos novos
    updated = 0
    added = 0
    for p in new_products:
        p_id = p.get("id")
        if not p_id:
            continue
        if p_id in existing_dict:
            existing_dict[p_id] = p
            updated += 1
        else:
            existing_dict[p_id] = p
            added += 1

    # Remover produtos muito antigos (mais de MAX_AGE_DAYS dias)
    cutoff = datetime.now() - timedelta(days=MAX_AGE_DAYS)
    removed = 0
    filtered = {}
    for p_id, p in existing_dict.items():
        # Unificar timestamps: usa last_seen ou data_coleta
        ts = p.get("last_seen") or p.get("data_coleta", "")
        if ts:
            try:
                ts_dt = datetime.fromisoformat(ts[:19])
                if ts_dt < cutoff:
                    removed += 1
                    continue
            except Exception:
                pass
        filtered[p_id] = p

    # Limitar tamanho do banco — manter os mais recentes
    final_list = list(filtered.values())
    if len(final_list) > MAX_DB_SIZE:
        # Ordenar por last_seen (mais recentes primeiro) para garantir rotatividade
        def sort_key(p):
            ts = p.get("last_seen") or p.get("data_coleta", "")
            return ts if ts else "0"
        final_list.sort(key=sort_key, reverse=True)
        final_list = final_list[:MAX_DB_SIZE]

    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

    logger.info(
        f"Sincronização concluída: +{added} novos, ~{updated} atualizados, "
        f"-{removed} expirados. Total no banco: {len(final_list)}"
    )


if __name__ == "__main__":
    sync()
