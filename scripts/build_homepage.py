import os
import json
import unicodedata
import random
from pathlib import Path
from logger import logger

BASE_URL = "https://comparapreco.github.io/"
ROOT = Path(__file__).resolve().parents[1] if "__file__" in locals() else Path(".")

# Configuração Portal Único
BASE_URL = "https://comparapreco.github.io/"

def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.lower().replace(' ', '-')
    return ''.join(c for c in text if c.isalnum() or c == '-')

def build_homepage(input_path: str, template_path: str, output_path: str) -> None:
    logger.info(f"Construindo página inicial dinâmica a partir de {input_path}...")
    
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
        logger.warning("Nenhum produto encontrado para a homepage.")
        return

    # Ordenar por desconto
    sorted_products = sorted(products, key=lambda x: x.get("custom_discount_pct", 0), reverse=True)
    
    # DIVERSIFICAÇÃO: Remover suplementos do topo e garantir variedade
    FORBIDDEN_HERO = ["whey", "creatina", "dark lab", "suplemento"]
    diversified_top = []
    seen_categories = {}
    
    for p in sorted_products:
        name_lower = p.get("name", "").lower()
        if any(term in name_lower for term in FORBIDDEN_HERO):
            continue
            
        cat = p.get("custom_category_slug", "outros")
        seen_categories[cat] = seen_categories.get(cat, 0) + 1
        
        # Máximo de 2 por categoria no topo para máxima variedade
        if seen_categories[cat] <= 2:
            diversified_top.append(p)
        if len(diversified_top) >= 30:
            break
            
    # Selecionar o destaque (Hero Section)
    # ROTATIVIDADE MÁXIMA: Usamos a hora atual como semente para garantir que o destaque mude a cada execução,
    # mas que seja consistente dentro de uma mesma rodada de geração.
    import time
    random.seed(int(time.time()))
    
    # Selecionamos entre os candidatos diversificados para o destaque
    top_candidates = diversified_top[:15]
    hero_product = random.choice(top_candidates)
    logger.info(f"Destaque rotativo escolhido: {hero_product.get('name')} (ID: {hero_product.get('id')})")
    
    # Remover o escolhido da lista para não repetir no grid logo abaixo
    remaining_products = [p for p in sorted_products if p['id'] != hero_product['id']]
    
    # Frases dinâmicas para o destaque
    badges = ["🔥 DESTAQUE DO DIA", "⚡ PREÇO BAIXOU!", "✨ NOVIDADE NO RADAR", "💎 ACHADO IMPERDÍVEL", "🚀 MELHOR DESCONTO"]
    catchy_phrases = [
        "Aproveite o maior desconto de hoje no Compara Preço!",
        "Economize agora com esta oferta selecionada pelo nosso robô.",
        "Preço imbatível detectado! Confira os detalhes abaixo.",
        "Não perca essa oportunidade de pagar menos hoje.",
        "Oferta fresquinha saindo do forno para você."
    ]
    
    p = hero_product
    p_name = p.get("name") or p.get("title") or ""
    p_id = p.get("id", "")
    p_slug = slugify(p_name)
    p_cat = p.get("custom_category_slug", "outros")
    internal_url = f"ofertas/{p_cat}/{p_slug}-{p_id}.html"
    
    hero_html = '<div id="heroProduct" class="hero-placeholder" style="min-height: 450px; display: flex; align-items: center; justify-content: center; background: var(--card); border-radius: 16px; border: 1px solid var(--border);"><p>Carregando as melhores ofertas do dia...</p></div>'

    # Grid de produtos - agora gerenciado pelo app.js para ser 100% dinâmico
    products_html = '<div id="featuredGrid" class="products-grid"></div>'
    
    seo_title = "Radar Ninja — As Melhores Ofertas do Mercado Livre Hoje"
    meta_description = "Radar Ninja: O seu rastreador de ofertas em tempo real. Economize com as melhores ofertas curadas do Mercado Livre com descontos de até 70%."
    canonical_url = BASE_URL
    
    # Carregar o menu de exploração
    explorar_menu_html = ""
    explorar_menu_path = "templates/explorar_menu.html"
    if os.path.exists(explorar_menu_path):
        try:
            with open(explorar_menu_path, "r", encoding="utf-8") as f:
                explorar_menu_html = f.read()
        except Exception as e:
            logger.warning(f"Não foi possível carregar o menu de exploração: {e}")
    
    content = template.replace("{{seo.title}}", seo_title)
    content = content.replace("{{meta.description}}", meta_description)
    content = content.replace("{{canonical.url}}", canonical_url)
    content = content.replace("{{hero_section}}", hero_html)
    content = content.replace("{{featured_products_grid}}", products_html)
    content = content.replace("{{explorar_menu}}", explorar_menu_html)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Homepage dinâmica gerada com sucesso: {output_path}")

if __name__ == "__main__":
    build_homepage("data/database/all_products.json", "templates/homepage.html", "index.html")
