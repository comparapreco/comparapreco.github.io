import os
import json
import markdown
import re
from pathlib import Path
from logger import logger

BASE_URL = "https://comparapreco.github.io/"

def generate_hubs():
    config_path = "config/hubs.json"
    template_path = "templates/hub_template.html"
    all_products_path = "data/database/all_products.json"
    
    if not os.path.exists(config_path):
        logger.error(f"Arquivo de configuração {config_path} não encontrado.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        hubs_config = json.load(f)

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    with open(all_products_path, "r", encoding="utf-8") as f:
        all_products = json.load(f)

    for slug, config in hubs_config.items():
        logger.info(f"Gerando Hub para a categoria: {slug}")
        
        output_dir = f"categorias/{slug}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Conteúdo do Guia
        hub_content_html = ""
        if os.path.exists(config['guide_path']):
            with open(config['guide_path'], "r", encoding="utf-8") as f:
                guide_md = f.read()
            hub_content_html = markdown.markdown(guide_md)
        else:
            logger.warning(f"Guia não encontrado: {config['guide_path']}")

        # 2. FAQ
        faq_html = ""
        if os.path.exists(config['faq_path']):
            with open(config['faq_path'], "r", encoding="utf-8") as f:
                faq_html = f.read()
        
        # 3. Links Relacionados (Produtos)
        related_links_html = ""
        cat_products = [p for p in all_products if p.get('custom_category_slug') == slug]
        cat_products_sorted = sorted(cat_products, key=lambda x: x.get('custom_discount_pct', 0), reverse=True)[:5]

        for p in cat_products_sorted:
            product_name = p.get('name', '')
            product_url = p.get('permalink', '')
            if product_name and product_url:
                related_links_html += f'<li><a href="../../{product_url}">{product_name}</a></li>\n'
        
        # 4. Links de Comparativos (da config)
        for comp in config.get('related_comparisons', []):
            related_links_html += f'<li><a href="../../{comp["url"]}">{comp["title"]}</a></li>\n'

        # 5. Schema FAQ (Opcional por enquanto, se existir arquivo JSON)
        faq_schema_json = ""
        schema_path = f"data/schema/{slug}-faq-schema.json"
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_data = json.load(f)
            faq_schema_json = json.dumps(schema_data, ensure_ascii=False, indent=2)[1:-1]

        # Substituições
        page_content = template.replace("{{seo.title}}", config['title'])
        page_content = page_content.replace("{{meta.description}}", config['description'])
        page_content = page_content.replace("{{canonical.url}}", f"{BASE_URL}categorias/{slug}/")
        page_content = page_content.replace("{{og.image}}", f"{BASE_URL}{config['og_image']}")
        page_content = page_content.replace("{{hub.content}}", hub_content_html)
        page_content = page_content.replace("{{faq.content}}", faq_html)
        page_content = page_content.replace("{{faq.schema}}", faq_schema_json)
        page_content = page_content.replace("{{related.links}}", related_links_html)
        page_content = page_content.replace("Celulares", slug.replace("-", " ").title()) # Ajuste dinâmico do breadcrumb/menu se necessário

        with open(f"{output_dir}/index.html", "w", encoding="utf-8") as f:
            f.write(page_content)
        
        logger.info(f"Hub {slug} gerado com sucesso.")

if __name__ == "__main__":
    generate_hubs()
