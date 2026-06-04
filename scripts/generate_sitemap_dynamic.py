import os
from datetime import datetime

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base_url = "https://comparapreco.github.io"

def generate_sitemap():
    urls = []
    
    # Adicionar páginas principais
    main_pages = [
        "",
        "/ofertas-hoje/",
        "/noticias/",
        "/categorias/",
        "/sobre/",
        "/contato/",
        "/privacidade/",
        "/disclaimer/"
    ]
    
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    
    for page in main_pages:
        urls.append(f"""  <url>
    <loc>{base_url}{page}</loc>
    <lastmod>{now}</lastmod>
    <priority>1.0</priority>
  </url>""")

    # Varrer ofertas
    ofertas_dir = os.path.join(base_dir, 'ofertas')
    for root, dirs, files in os.walk(ofertas_dir):
        for file in files:
            if file.endswith('.html'):
                rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                url_path = "/" + rel_path.replace(os.sep, '/')
                if url_path.endswith('index.html'):
                    url_path = url_path[:-10]
                
                urls.append(f"""  <url>
    <loc>{base_url}{url_path}</loc>
    <lastmod>{now}</lastmod>
    <priority>0.8</priority>
  </url>""")

    # Varrer notícias
    noticias_dir = os.path.join(base_dir, 'noticias')
    for root, dirs, files in os.walk(noticias_dir):
        for file in files:
            if file.endswith('.html'):
                rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                url_path = "/" + rel_path.replace(os.sep, '/')
                if url_path.endswith('index.html'):
                    url_path = url_path[:-10]
                
                urls.append(f"""  <url>
    <loc>{base_url}{url_path}</loc>
    <lastmod>{now}</lastmod>
    <priority>0.7</priority>
  </url>""")

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"\n".join(urls)}
</urlset>"""

    with open(os.path.join(base_dir, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    
    print(f"Sitemap dinâmico gerado com {len(urls)} URLs.")

if __name__ == "__main__":
    generate_sitemap()
