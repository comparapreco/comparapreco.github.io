import json
import os
from pathlib import Path
from logger import logger

ROOT = Path(__file__).resolve().parents[1]

def detect_gaps():
    logger.info("Analisando lacunas de conteúdo no portal...")
    
    with open(ROOT / "data" / "database" / "all_products.json", 'r') as f:
        products = json.load(f)
    
    # Agrupar por categoria
    cats = {}
    for p in products:
        c = p.get("custom_category_slug", "geral")
        if c not in cats: cats[c] = []
        cats[c].append(p)
        
    gaps = {
        "empty_categories": [],
        "low_content_brands": [],
        "missing_comparisons": [],
        "missing_rankings": []
    }
    
    # 1. Identificar categorias com poucos produtos
    for cat, items in cats.items():
        if len(items) < 5:
            gaps["empty_categories"].append(cat)
            
    # 2. Identificar se faltam rankings para categorias com muitos produtos
    for cat, items in cats.items():
        ranking_file = ROOT / "melhores-2026" / f"melhores-{cat}-2026.html"
        if len(items) >= 3 and not ranking_file.exists():
            gaps["missing_rankings"].append(cat)
            
    # 3. Identificar produtos populares sem comparativos (simulação)
    # Aqui poderíamos cruzar com dados de "mais clicados" no futuro
    
    return gaps

def auto_expand(gaps):
    if gaps["missing_rankings"]:
        logger.info(f"Auto-expansão: Gerando {len(gaps['missing_rankings'])} rankings faltantes...")
        # O script generate_programmatic_seo.py já deve cuidar disso se rodado novamente,
        # mas aqui poderíamos forçar a criação de conteúdos específicos.
        pass

if __name__ == "__main__":
    gaps = detect_gaps()
    logger.info(f"Lacunas encontradas: {gaps}")
    auto_expand(gaps)
    with open(ROOT / "data" / "content_gaps.json", 'w') as f:
        json.dump(gaps, f, indent=2)
