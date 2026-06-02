import os
import json
from logger import logger

def clean_orphans():
    orphan_path = "data/orphan_pages.json"
    if not os.path.exists(orphan_path):
        logger.error("Arquivo de páginas órfãs não encontrado.")
        return

    with open(orphan_path, "r", encoding="utf-8") as f:
        orphans = json.load(f)

    logger.info(f"Iniciando remoção de {len(orphans)} páginas órfãs...")
    
    removed_count = 0
    for file_path in orphans:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                removed_count += 1
            except Exception as e:
                logger.error(f"Erro ao remover {file_path}: {e}")

    logger.info(f"Limpeza concluída: {removed_count} arquivos removidos.")
    
    # Atualizar Sitemaps
    try:
        from generate_sitemaps import generate_all_sitemaps
        generate_all_sitemaps()
        logger.info("Sitemaps atualizados com sucesso.")
    except ImportError:
        logger.warning("Script generate_sitemaps não encontrado, sitemaps não atualizados.")

if __name__ == "__main__":
    clean_orphans()
