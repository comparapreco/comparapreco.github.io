import os
import json
from datetime import datetime
from logger import logger

def generate_sitemap():
    logger.info("Gerando sitemap.xml defensivo...")
    base_url = "https://comparadordepreco.github.io/compara"
    urls = [
        {"loc": f"{base_url}/", "priority": "1.0", "changefreq": "daily"},
        {"loc": f"{base_url}/noticias/", "priority": "0.8", "changefreq": "daily"},
        {"loc": f"{base_url}/melhores-ofertas/", "priority": "0.9", "changefreq": "hourly"},
    ]
    
    seen_locs = {u["loc"] for u in urls}
    
    # Adicionar produtos do banco
    db_path = "data/database/all_products.json"
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            products = json.load(f)
            for p in products:
                # Gerar slug limpo para URL
                slug = p.get('slug') or p.get('id')
                category = p.get('category', 'geral').lower().replace(' ', '-')
                loc = f"{base_url}/ofertas/{category}/{slug}.html"
                if loc not in seen_locs:
                    urls.append({"loc": loc, "priority": "0.6", "changefreq": "weekly"})
                    seen_locs.add(loc)

    # Gerar XML
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    
    for u in urls:
        xml_content.append(f'    <url>')
        xml_content.append(f'        <loc>{u["loc"]}</loc>')
        xml_content.append(f'        <lastmod>{now}</lastmod>')
        xml_content.append(f'        <changefreq>{u["changefreq"]}</changefreq>')
        xml_content.append(f'        <priority>{u["priority"]}</priority>')
        xml_content.append(f'    </url>')
    
    xml_content.append('</urlset>')
    
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(xml_content))
    logger.info(f"Sitemap gerado com {len(urls)} URLs únicas.")

if __name__ == "__main__":
    generate_sitemap()
