import json
import os
from pathlib import Path
from logger import logger

ROOT = Path(__file__).resolve().parents[1]

def monitor_indexation():
    logger.info("Monitorando Indexação e Cobertura...")
    
    # Simulação de dados do Search Console (No mundo real, usaríamos a API do GSC)
    # Por enquanto, rastreamos o que foi gerado vs o que está no sitemap
    
    total_generated = len(list(ROOT.rglob("*.html")))
    
    # Carregar sitemap para ver o que "deveria" estar indexado
    urls_in_sitemap = 0
    sitemaps = list(ROOT.glob("sitemap-*.xml"))
    for sm in sitemaps:
        with open(sm, 'r') as f:
            urls_in_sitemap += f.read().count("<loc>")
            
    index_stats = {
        "total_generated": total_generated,
        "total_in_sitemap": urls_in_sitemap,
        "indexation_ratio": round((urls_in_sitemap / total_generated) * 100, 2) if total_generated > 0 else 0,
        "categories_coverage": {}
    }
    
    # Cobertura por categoria
    cat_dir = ROOT / "categorias"
    for d in cat_dir.iterdir():
        if d.is_dir():
            count = len(list(d.glob("*.html")))
            index_stats["categories_coverage"][d.name] = count

    with open(ROOT / "data" / "index_stats.json", 'w') as f:
        json.dump(index_stats, f, indent=2)
    logger.info("Estatísticas de indexação atualizadas.")

if __name__ == "__main__":
    monitor_indexation()
