import os
import json
from datetime import datetime

BASE_URL = "https://comparapreco.github.io/"

def generate_sitemap(filename, urls):
    content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        content += '  <url>\n'
        content += f'    <loc>{url}</loc>\n'
        content += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
        content += '    <changefreq>daily</changefreq>\n'
        content += '    <priority>0.8</priority>\n'
        content += '  </url>\n'
    content += '</urlset>'
    
    # Usar caminho relativo ao diretório raiz do repositório
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(root_dir, filename)
    with open(file_path, "w") as f:
        f.write(content)
    print(f"Sitemap {filename} gerado com {len(urls)} URLs.")

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 1. Sitemap de Guias
    guias_dir = os.path.join(root_dir, "guias")
    guia_urls = []
    if os.path.exists(guias_dir):
        for d in os.listdir(guias_dir):
            if os.path.isdir(os.path.join(guias_dir, d)):
                guia_urls.append(f"{BASE_URL}guias/{d}/")
    generate_sitemap("sitemap-guias.xml", guia_urls)

    # 2. Sitemap de Categorias
    cat_dir = os.path.join(root_dir, "categorias")
    cat_urls = []
    if os.path.exists(cat_dir):
        for d in os.listdir(cat_dir):
            if os.path.isdir(os.path.join(cat_dir, d)):
                cat_urls.append(f"{BASE_URL}categorias/{d}/")
    generate_sitemap("sitemap-categorias.xml", cat_urls)

    # 3. Sitemap de Notícias
    noticias_dir = os.path.join(root_dir, "noticias")
    noticia_urls = [f"{BASE_URL}noticias/"] # Hub principal
    # Se houver notícias individuais no futuro, adicionar aqui
    generate_sitemap("sitemap-noticias.xml", noticia_urls)

    # 4. Sitemap de Produtos
    produtos_urls = []
    ofertas_dir = os.path.join(root_dir, "ofertas")
    if os.path.exists(ofertas_dir):
        for root, dirs, files in os.walk(ofertas_dir):
            for file in files:
                if file.endswith(".html"):
                    rel_path = os.path.relpath(os.path.join(root, file), ofertas_dir)
                    produtos_urls.append(f"{BASE_URL}ofertas/{rel_path}")
    generate_sitemap("sitemap-produtos.xml", produtos_urls)

    # 5. Sitemap Index
    index_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    index_content += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for s in ["sitemap-guias.xml", "sitemap-categorias.xml", "sitemap-noticias.xml", "sitemap-produtos.xml"]:
        index_content += '  <sitemap>\n'
        index_content += f'    <loc>{BASE_URL}{s}</loc>\n'
        index_content += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
        index_content += '  </sitemap>\n'
    index_content += '</sitemapindex>'
    
    with open(os.path.join(root_dir, "sitemap.xml"), "w") as f:
        f.write(index_content)
    print("Sitemap index gerado.")

if __name__ == "__main__":
    main()
