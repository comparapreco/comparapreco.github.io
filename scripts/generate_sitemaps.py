#!/usr/bin/env python3
"""
Gerador Automático de Sitemaps - Compara Preço
Detecta automaticamente todos os posts, categorias e páginas e gera um sitemap index completo.
"""
import os
import re
from datetime import datetime
from pathlib import Path

BASE_URL = "https://comparapreco.github.io"
ROOT = Path(__file__).resolve().parents[1]
NOW_DATE = datetime.now().strftime("%Y-%m-%d")

def write_sitemap(filename: str, urls: list) -> None:
    """Escreve um arquivo sitemap XML com as URLs fornecidas."""
    if not urls:
        return
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{u['loc']}</loc>")
        lines.append(f"    <lastmod>{u.get('lastmod', NOW_DATE)}</lastmod>")
        lines.append(f"    <changefreq>{u.get('changefreq', 'weekly')}</changefreq>")
        lines.append(f"    <priority>{u.get('priority', '0.6')}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    out_path = ROOT / filename
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] {filename} -> {len(urls)} URLs")

def collect_urls():
    """Coleta todas as URLs do site escaneando as pastas."""
    all_urls = {
        "paginas": [],
        "noticias": [],
        "produtos": [],
        "categorias": [],
        "rankings": []
    }

    # 1. Páginas Estáticas na raiz
    for f in ROOT.glob("*.html"):
        if f.name == "index.html":
            all_urls["paginas"].append({"loc": f"{BASE_URL}/", "priority": "1.0", "changefreq": "daily"})
        else:
            all_urls["paginas"].append({"loc": f"{BASE_URL}/{f.name}", "priority": "0.5", "changefreq": "weekly"})

    # 2. Notícias e Posts
    posts_dir = ROOT / "noticias" / "posts"
    if posts_dir.exists():
        for f in posts_dir.glob("*.html"):
            all_urls["noticias"].append({
                "loc": f"{BASE_URL}/noticias/posts/{f.name}",
                "priority": "0.8",
                "changefreq": "monthly"
            })
    
    # Hub de notícias
    if (ROOT / "noticias" / "index.html").exists():
        all_urls["noticias"].append({"loc": f"{BASE_URL}/noticias/", "priority": "0.9", "changefreq": "daily"})

    # 3. Categorias
    cat_dir = ROOT / "categorias"
    if cat_dir.exists():
        # Incluir a página principal de categorias
        if (cat_dir / "index.html").exists():
            all_urls["categorias"].append({
                "loc": f"{BASE_URL}/categorias/",
                "priority": "0.9",
                "changefreq": "weekly"
            })
            
        for d in cat_dir.iterdir():
            # Validar se é um diretório e se possui o index.html gerado
            if d.is_dir() and (d / "index.html").exists():
                # Evitar incluir pastas de sistema ou temporárias
                if d.name in ["assets", "css", "js"]: continue
                
                all_urls["categorias"].append({
                    "loc": f"{BASE_URL}/categorias/{d.name}/",
                    "priority": "0.8",
                    "changefreq": "daily"
                })

    # 4. Rankings
    rank_dir = ROOT / "melhores-2026"
    if rank_dir.exists():
        for f in rank_dir.glob("*.html"):
            all_urls["rankings"].append({
                "loc": f"{BASE_URL}/melhores-2026/{f.name}",
                "priority": "0.9",
                "changefreq": "weekly"
            })

    # 5. Produtos/Ofertas (se houver pastas)
    for folder in ["ofertas", "produtos"]:
        p_dir = ROOT / folder
        if p_dir.exists():
            for f in p_dir.rglob("*.html"):
                rel_path = f.relative_to(ROOT)
                all_urls["produtos"].append({
                    "loc": f"{BASE_URL}/{rel_path}",
                    "priority": "0.7",
                    "changefreq": "daily"
                })

    return all_urls

def generate_index(sitemaps):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for s in sitemaps:
        lines.append("  <sitemap>")
        lines.append(f"    <loc>{BASE_URL}/{s}</loc>")
        lines.append(f"    <lastmod>{NOW_DATE}</lastmod>")
        lines.append("  </sitemap>")
    lines.append("</sitemapindex>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] sitemap.xml (index com {len(sitemaps)} sitemaps)")

def main():
    print("Gerando sitemaps completos...")
    urls = collect_urls()
    
    active_sitemaps = []
    for key, items in urls.items():
        if items:
            filename = f"sitemap-{key}.xml"
            write_sitemap(filename, items)
            active_sitemaps.append(filename)
    
    generate_index(active_sitemaps)
    total = sum(len(v) for v in urls.values())
    print(f"Total de URLs indexadas: {total}")

if __name__ == "__main__":
    main()
