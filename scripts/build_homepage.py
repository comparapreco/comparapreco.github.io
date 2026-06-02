import os
import json
import unicodedata
import random
from pathlib import Path
from logger import logger

ROOT = Path(__file__).resolve().parents[1] if "__file__" in locals() else Path(".")
BASE_URL = "https://comparapreco.github.io/"

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.lower().replace(' ', '-')
    return ''.join(c for c in text if c.isalnum() or c == '-')

def build_homepage(input_path, template_path, output_path):
    logger.info(f"Construindo home diversificada a partir de {input_path}...")
    if not os.path.exists(template_path):
        logger.error(f"Template {template_path} não encontrado!")
        return
    
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    products = []
    if os.path.exists(input_path):
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                products = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar {input_path}: {e}")

    if not products:
        logger.warning("Nenhum produto para a home.")
        return

    sorted_products = sorted(products, key=lambda x: (x.get("quality_score", 0), x.get("custom_discount_pct", 0)), reverse=True)

    diversified = []
    brand_counts = {}
    for p in sorted_products:
        brand = p.get("brand_name") or "generico"
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
        if brand_counts[brand] <= 2:
            diversified.append(p)
        if len(diversified) >= 50:
            break

    if len(diversified) < 20:
        for p in sorted_products:
            if p not in diversified:
                diversified.append(p)
            if len(diversified) >= 40: break

    random.seed(os.getpid())
    hero_product = random.choice(diversified[:10]) if diversified else sorted_products[0]

    template = template.replace("{{hero_id}}", hero_product.get("id", ""))
    
    # CORREÇÃO: Tratar diretório vazio
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template)
    
    logger.info(f"Home gerada com {len(diversified)} produtos diversificados.")

if __name__ == "__main__":
    build_homepage("data/database/all_products.json", "templates/index.html", "index.html")
