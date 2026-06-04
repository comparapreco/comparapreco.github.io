import os
import json
from typing import List, Dict, Any
from logger import logger

BASE_URL = "https://comparapreco.github.io/"

def build_category_page(category_slug: str, products: List[Dict[str, Any]], template_path: str, output_dir: str) -> None:
    logger.info(f"Gerando página para a categoria: {category_slug}")
    
    if not os.path.exists(template_path):
        logger.error(f"Template {template_path} não encontrado!")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
        
    category_name = category_slug.replace("-", " ").title()
    
    def _safe_url(p):
        aff = p.get('custom_affiliate_url', '')
        if aff and '/social/' not in aff and True:
            return aff
        return p.get('permalink', '')

    # Renderizar produtos da categoria
    category_products_html = ""
    for idx, p in enumerate(products):
        # Pular produtos sem imagem ou link básico
        img_url = p.get("image") or p.get("thumbnail")
        product_url = _safe_url(p)
        
        if not img_url or not product_url:
            continue

        discount = p.get("custom_discount_pct", 0)
        
        # Lógica de Selos Dinâmicos
        extra_badge = ""
        if discount >= 60:
            extra_badge = '<span class="badge badge-menor-preco">💎 MENOR PREÇO</span>'
        elif discount >= 45:
            extra_badge = '<span class="badge badge-baixou">📉 BAIXOU!</span>'
        elif idx < 3:
            extra_badge = '<span class="badge badge-promo-dia">🌟 PROMOÇÃO DO DIA</span>'

        category_products_html += f"""
        <div class="product-card">
            <span class="badge discount-badge">↓ {discount}% OFF</span>
            {extra_badge}
            <div class="card-img"><img src="{img_url}" alt="{p.get("name", "")}"></div>
            <h3>{p.get("name", "")[:50]}...</h3>
            <div class="price-tag" style="font-size: 20px;">R$ {p.get("price", 0):.2f} <span class="old-price" style="font-size: 14px;">R$ {p.get("originalPrice", 0):.2f}</span></div>
            <a href="{product_url}" class="btn" style="width: 100%; text-align: center;" target="_blank">Comprar</a>
        </div>
        """
        
    # SEO para categorias (Fase 1)
    seo_title = f"Ofertas de {category_name} com Desconto no Compara Preço"
    meta_description = f"Compare os melhores {category_slug.replace("-", " ").title()}, veja preços atualizados, avaliações e ofertas das principais lojas."
    canonical_url = f"{BASE_URL}categorias/{category_slug}/"

    # Substituições no template
    page_content = template.replace("{{seo.title}}", seo_title)
    page_content = page_content.replace("{{meta.description}}", meta_description)
    page_content = page_content.replace("{{canonical.url}}", canonical_url)
    page_content = page_content.replace("{{category.name}}", category_name)
    page_content = page_content.replace("{{category.slug}}", category_slug)
    page_content = page_content.replace("{{category.products}}", category_products_html)

    # Marcar categoria ativa no menu
    categories_list = ["tecnologia", "gamer", "casa", "eletrodomesticos", "pet", "beleza", "fitness", "auto", "moveis"]
    for cat in categories_list:
        placeholder = f"{{{{cat_{cat}_active}}}}"
        active_class = "active" if cat == category_slug else ""
        page_content = page_content.replace(placeholder, active_class)
    
    # Salvar página
    page_path = os.path.join(output_dir, category_slug, "index.html")
    os.makedirs(os.path.dirname(page_path), exist_ok=True)
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(page_content)
    logger.info(f"Página de categoria gerada: {page_path}")

def build_all_category_pages(input_path: str, template_path: str, output_dir: str) -> None:
    logger.info(f"Gerando páginas de categorias a partir de {input_path}...")
    
    products = []
    if os.path.exists(input_path):
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                products = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar {input_path}: {e}")
    
    if not products:
        return
        
    categories: Dict[str, List[Dict[str, Any]]] = {}
    categories: Dict[str, List[Dict[str, Any]]] = {}
    brands: Dict[str, List[Dict[str, Any]]] = {}
    
    for product in products:
        # Categorias
        cat_slug = product.get("custom_category_slug", "outros")
        if cat_slug not in categories: categories[cat_slug] = []
        categories[cat_slug].append(product)
        
        # Marcas (extrair do nome se não houver campo específico)
        name_lower = (product.get("name") or "").lower()
        for brand in ["samsung", "motorola", "lenovo", "lg", "jbl", "apple", "philco", "asus"]:
            if brand in name_lower:
                if brand not in brands: brands[brand] = []
                brands[brand].append(product)
                break
        
    # Gerar páginas de categorias
    for slug, cat_products in categories.items():
        build_category_page(slug, cat_products, template_path, output_dir)
        
    # Gerar páginas de marcas (Hub de Marcas)
    for brand, brand_products in brands.items():
        build_category_page(brand, brand_products, template_path, output_dir)

if __name__ == "__main__":
    build_all_category_pages("data/database/all_products.json", "templates/category_template.html", "categorias")
