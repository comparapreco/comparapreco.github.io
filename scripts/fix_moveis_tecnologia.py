#!/usr/bin/env python3
"""
Script para:
1. Criar a página /categorias/moveis/ (corrigir erro 404)
2. Atualizar a página /categorias/tecnologia/ com produtos reais
"""
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PRODUCTS_FILE = BASE_DIR / "data" / "database" / "all_products.json"
TEMPLATE_FILE = BASE_DIR / "templates" / "category_template.html"
CATEGORIAS_DIR = BASE_DIR / "categorias"
BASE_URL = "https://comparapreco.github.io/"

def load_products():
    with open(PRODUCTS_FILE, encoding="utf-8") as f:
        return json.load(f)

def load_template():
    with open(TEMPLATE_FILE, encoding="utf-8") as f:
        return f.read()

def safe_url(p):
    url = p.get("custom_affiliate_url", "") or p.get("permalink", "")
    if url and "mercadolivre.com" in url and "matt_tool=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}matt_tool=vendas0nline"
    return url

def build_product_card(p, idx):
    img_url = p.get("image") or p.get("thumbnail", "")
    product_url = safe_url(p)
    if not img_url or not product_url:
        return ""
    
    discount = p.get("custom_discount_pct", 0) or 0
    name = p.get("name", "")
    price = p.get("price", 0) or 0
    original_price = p.get("originalPrice") or p.get("original_price") or 0

    # Selos dinâmicos
    extra_badge = ""
    if discount >= 60:
        extra_badge = '<span class="badge badge-menor-preco">💎 MENOR PREÇO</span>'
    elif discount >= 45:
        extra_badge = '<span class="badge badge-baixou">📉 BAIXOU!</span>'
    elif idx < 3:
        extra_badge = '<span class="badge badge-promo-dia">🌟 PROMOÇÃO DO DIA</span>'

    name_short = name[:50] + "..." if len(name) > 50 else name

    return f"""
        <div class="product-card">
            <span class="badge discount-badge">↓ {discount}% OFF</span>
            {extra_badge}
            <div class="card-img"><img src="{img_url}" alt="{name}" loading="lazy"></div>
            <h3>{name_short}</h3>
            <div class="price-tag" style="font-size: 20px;">R$ {float(price):.2f} <span class="old-price" style="font-size: 14px;">R$ {float(original_price):.2f}</span></div>
            <a href="{product_url}" class="btn" style="width: 100%; text-align: center;" target="_blank">Comprar</a>
        </div>"""

def generate_page(category_slug, category_name, category_icon, products, template):
    """Gera uma página de categoria a partir do template."""
    # Filtrar produtos válidos e ordenar por desconto
    valid_products = [p for p in products if (p.get("image") or p.get("thumbnail")) and safe_url(p)]
    valid_products.sort(key=lambda p: p.get("custom_discount_pct", 0) or 0, reverse=True)

    # Gerar HTML dos produtos
    products_html = ""
    for idx, p in enumerate(valid_products):
        products_html += build_product_card(p, idx)

    if not products_html:
        products_html = '<p style="text-align:center;padding:40px;grid-column:1/-1;color:var(--text-muted);">Em breve novos produtos nesta categoria.</p>'

    # Substituições no template
    page = template
    page = page.replace("{{seo.title}}", f"Ofertas de {category_name} com Desconto no Compara Preço")
    page = page.replace("{{meta.description}}", f"Encontre as melhores ofertas de {category_name} no Mercado Livre. Descontos incríveis e produtos selecionados para você economizar.")
    page = page.replace("{{canonical.url}}", f"{BASE_URL}categorias/{category_slug}/")
    page = page.replace("{{category.name}}", category_name)
    page = page.replace("{{category.slug}}", category_slug)
    page = page.replace("{{category.products}}", products_html)

    # Marcar categoria ativa no menu
    categories_list = ["tecnologia", "gamer", "casa", "eletrodomesticos", "pet", "beleza", "fitness", "auto", "moveis"]
    for cat in categories_list:
        placeholder = f"{{{{cat_{cat}_active}}}}"
        active_class = "active" if cat == category_slug else ""
        page = page.replace(placeholder, active_class)

    # Salvar
    output_path = CATEGORIAS_DIR / category_slug / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"✅ Página gerada: {output_path} ({len(valid_products)} produtos)")
    return output_path

def main():
    print("Carregando produtos e template...")
    all_products = load_products()
    template = load_template()

    # =========================================================
    # 1. CRIAR PÁGINA DE MÓVEIS
    # =========================================================
    # Palavras-chave para móveis (inclui produtos da categoria 'casa' que são móveis)
    moveis_keywords = [
        'sofa', 'sofá', 'cama', 'mesa', 'cadeira', 'armário', 'armario',
        'guarda-roupa', 'guarda roupa', 'estante', 'rack', 'colchao', 'colchão',
        'escrivaninha', 'poltrona', 'beliche', 'criado-mudo', 'criado mudo',
        'prateleira', 'painel', 'buffet', 'aparador', 'penteadeira'
    ]

    moveis_products = []
    for p in all_products:
        name_lower = (p.get("name") or "").lower()
        cat = p.get("custom_category_slug", "")
        if any(kw in name_lower for kw in moveis_keywords):
            moveis_products.append(p)

    # Se poucos produtos, buscar também na categoria 'casa' com desconto alto
    if len(moveis_products) < 6:
        casa_products = [p for p in all_products if p.get("custom_category_slug") == "casa"
                         and p not in moveis_products]
        moveis_products.extend(casa_products)

    print(f"\nMóveis: {len(moveis_products)} produtos encontrados")
    generate_page("moveis", "Móveis", "🛋️", moveis_products, template)

    # =========================================================
    # 2. ATUALIZAR PÁGINA DE TECNOLOGIA
    # =========================================================
    # Tecnologia = informatica + celulares + tv-e-video
    tech_slugs = ["informatica", "celulares", "tv-e-video"]
    tech_products = [p for p in all_products if p.get("custom_category_slug") in tech_slugs]

    print(f"\nTecnologia: {len(tech_products)} produtos encontrados")
    generate_page("tecnologia", "Tecnologia", "📱", tech_products, template)

    print("\n✅ Concluído!")

if __name__ == "__main__":
    main()
