"""
generate_hubs.py
Gerador genérico de Hubs de categoria para o Radar Ninja.
Lê config/hubs.json e gera um index.html para cada categoria
usando o template único templates/hub_template.html.
Para adicionar uma nova categoria: edite apenas config/hubs.json.
"""

import os
import json
import markdown
from pathlib import Path

try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

BASE_URL = "https://comparapreco.github.io/"


def build_nav_tabs(hubs_config: dict, current_slug: str) -> str:
    """Gera as abas de navegação com a categoria atual marcada como 'active'."""
    tabs_html = ""
    for slug, config in hubs_config.items():
        icon = config.get("icon", "🔗")
        name = config.get("name", slug.replace("-", " ").title())
        active_class = " active" if slug == current_slug else ""
        tabs_html += f'<a class="cat-tab{active_class}" href="../../categorias/{slug}/">{icon} {name}</a>\n            '
    return tabs_html.strip()


def generate_hubs():
    config_path = "config/hubs.json"
    template_path = "templates/hub_template.html"
    all_products_path = "data/database/all_products.json"

    if not os.path.exists(config_path):
        logger.error(f"Arquivo de configuração {config_path} não encontrado.")
        return False

    if not os.path.exists(template_path):
        logger.error(f"Template {template_path} não encontrado.")
        return False

    with open(config_path, "r", encoding="utf-8") as f:
        hubs_config = json.load(f)

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Carrega o banco de produtos (pode não existir em ambiente de teste)
    all_products = []
    if os.path.exists(all_products_path):
        with open(all_products_path, "r", encoding="utf-8") as f:
            all_products = json.load(f)
    else:
        logger.warning(f"Banco de dados {all_products_path} não encontrado. Hubs serão gerados sem produtos dinâmicos.")

    hubs_gerados = 0

    for slug, config in hubs_config.items():
        logger.info(f"Gerando Hub para a categoria: {slug}")

        output_dir = f"categorias/{slug}"
        os.makedirs(output_dir, exist_ok=True)

        # 1. Nome legível da categoria
        hub_name = config.get("name", slug.replace("-", " ").title())

        # 2. Conteúdo do Guia (Markdown → HTML)
        hub_content_html = ""
        guide_path = config.get("guide_path", "")
        if guide_path and os.path.exists(guide_path):
            with open(guide_path, "r", encoding="utf-8") as f:
                guide_md = f.read()
            hub_content_html = markdown.markdown(guide_md, extensions=["tables"])
        else:
            logger.warning(f"Guia não encontrado: {guide_path}")
            hub_content_html = f"<p>Guia de compra para {hub_name} em breve.</p>"

        # 3. FAQ (HTML estático)
        faq_html = ""
        faq_path = config.get("faq_path", "")
        if faq_path and os.path.exists(faq_path):
            with open(faq_path, "r", encoding="utf-8") as f:
                faq_html = f.read()

        # 4. Links de Produtos Dinâmicos (top 5 com maior desconto na categoria)
        related_links_html = ""
        cat_products = [
            p for p in all_products
            if p.get("custom_category_slug") == slug
        ]
        cat_products_sorted = sorted(
            cat_products,
            key=lambda x: x.get("custom_discount_pct", 0),
            reverse=True
        )[:5]

        for p in cat_products_sorted:
            product_name = p.get("name", "")
            product_url = p.get("permalink", "")
            discount = p.get("custom_discount_pct", 0)
            if product_name and product_url:
                discount_badge = f' <span style="color:#22c55e;font-size:12px;">-{discount:.0f}%</span>' if discount > 0 else ""
                related_links_html += f'<li><a href="../../{product_url}">{product_name}{discount_badge}</a></li>\n'

        # 5. Links de Comparativos (da config)
        for comp in config.get("related_comparisons", []):
            related_links_html += f'<li><a href="../../{comp["url"]}">{comp["title"]}</a></li>\n'

        # 6. Schema FAQ (se existir arquivo JSON de schema)
        faq_schema_json = ""
        schema_path = f"data/schema/{slug}-faq-schema.json"
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_data = json.load(f)
            faq_schema_json = json.dumps(schema_data, ensure_ascii=False, indent=2)[1:-1]

        # 7. Abas de navegação dinâmicas
        nav_tabs_html = build_nav_tabs(hubs_config, slug)

        # 8. Substituições no template
        og_image = config.get("og_image", "assets/og-image.png")
        page_content = template
        page_content = page_content.replace("{{seo.title}}", config["title"])
        page_content = page_content.replace("{{meta.description}}", config["description"])
        page_content = page_content.replace("{{canonical.url}}", f"{BASE_URL}categorias/{slug}/")
        page_content = page_content.replace("{{og.image}}", f"{BASE_URL}{og_image}")
        page_content = page_content.replace("{{hub.name}}", hub_name)
        page_content = page_content.replace("{{hub.content}}", hub_content_html)
        page_content = page_content.replace("{{faq.content}}", faq_html)
        page_content = page_content.replace("{{faq.schema}}", faq_schema_json)
        page_content = page_content.replace("{{related.links}}", related_links_html)
        page_content = page_content.replace("{{nav.tabs}}", nav_tabs_html)

        output_path = f"{output_dir}/index.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(page_content)

        logger.info(f"✅ Hub '{hub_name}' gerado: {output_path}")
        hubs_gerados += 1

    logger.info(f"🎉 Sistema de Hubs concluído: {hubs_gerados} hubs gerados.")
    return True


if __name__ == "__main__":
    generate_hubs()
