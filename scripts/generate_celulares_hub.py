import os
import json
import markdown
from pathlib import Path
import re

BASE_URL = "https://comparapreco.github.io/"

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text

def generate_celulares_hub():
    # Caminhos dos arquivos
    template_path = "templates/hub_template.html"
    guide_md_path = "noticias/posts/como-escolher-um-celular-2026-guia-completo.md"
    faq_html_path = "noticias/posts/celulares-faq.html"
    faq_schema_path = "data/schema/celulares-faq-schema.json"
    all_products_path = "data/database/all_products.json"
    output_dir = "categorias/celulares"
    output_path = os.path.join(output_dir, "index.html")

    # Criar diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)

    # Carregar template do hub
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Carregar conteúdo do guia (Markdown para HTML)
    with open(guide_md_path, "r", encoding="utf-8") as f:
        guide_md = f.read()
    hub_content_html = markdown.markdown(guide_md)

    # Carregar HTML do FAQ
    with open(faq_html_path, "r", encoding="utf-8") as f:
        faq_html = f.read()

    # Carregar Schema FAQ
    with open(faq_schema_path, "r", encoding="utf-8") as f:
        faq_schema_data = json.load(f)
    faq_schema_json = json.dumps(faq_schema_data, ensure_ascii=False, indent=2)
    # Remover colchetes externos para injetar diretamente no array mainEntity
    faq_schema_json = faq_schema_json[1:-1] 

    # Carregar todos os produtos para links internos
    with open(all_products_path, "r", encoding="utf-8") as f:
        all_products = json.load(f)

    # Gerar links úteis (produtos e comparativos)
    related_links_html = ""
    # Exemplo: 5 melhores celulares da categoria
    celulares_products = [p for p in all_products if p.get('custom_category_slug') == 'celulares']
    # Ordenar por desconto ou algum critério de relevância
    celulares_products_sorted = sorted(celulares_products, key=lambda x: x.get('custom_discount_pct', 0), reverse=True)[:5]

    for p in celulares_products_sorted:
        product_name = p.get('name', '')
        product_url = p.get('permalink', '')
        if product_name and product_url:
            related_links_html += f'<li><a href="../../{product_url}">{product_name}</a></li>\n'
    
    # Adicionar links para comparativos (exemplo)
    related_links_html += '<li><a href="../../comparar/celulares-top-de-linha.html">Comparativo: Celulares Top de Linha</a></li>\n'
    related_links_html += '<li><a href="../../comparar/celulares-custo-beneficio.html">Comparativo: Celulares Custo-Benefício</a></li>\n'

    # SEO para o Hub de Celulares
    seo_title = "Celulares: Guia Completo, Ofertas e Comparativos | Radar Ninja"
    meta_description = "Encontre os melhores celulares, compare preços, veja guias de compra e as ofertas mais quentes de smartphones no Radar Ninja."
    canonical_url = f"{BASE_URL}categorias/celulares/"
    og_image = f"{BASE_URL}assets/images/celulares-hub-og.jpg" # Imagem Open Graph para o hub

    # Substituições no template
    page_content = template.replace("{{seo.title}}", seo_title)
    page_content = page_content.replace("{{meta.description}}", meta_description)
    page_content = page_content.replace("{{canonical.url}}", canonical_url)
    page_content = page_content.replace("{{og.image}}", og_image)
    page_content = page_content.replace("{{hub.content}}", hub_content_html)
    page_content = page_content.replace("{{faq.content}}", faq_html)
    page_content = page_content.replace("{{faq.schema}}", faq_schema_json)
    page_content = page_content.replace("{{related.links}}", related_links_html)

    # Salvar página final
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(page_content)

    print(f"Hub de Celulares gerado com sucesso em: {output_path}")

if __name__ == "__main__":
    generate_celulares_hub()
