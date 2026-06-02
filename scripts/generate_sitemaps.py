#!/usr/bin/env python3
"""
Gerador Automático de Sitemaps - Compara Preço
Detecta automaticamente novos posts, produtos e páginas e regenera todos os sitemaps.
Executado a cada hora via GitHub Actions.
"""
import os
import re
from datetime import datetime
from pathlib import Path

BASE_URL = "https://comparapreco.github.io"
ROOT = Path(__file__).resolve().parents[1]

# Configuração Multi-Site
SITE_KEY = os.environ.get("SITE_KEY")
if SITE_KEY:
    BASE_URL = f"https://comparapreco.github.io/sites/{SITE_KEY}"
    OUTPUT_ROOT = ROOT / "sites" / SITE_KEY
else:
    OUTPUT_ROOT = ROOT

NOW_DATE = datetime.now().strftime("%Y-%m-%d")
NOW_DATETIME = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")


def write_sitemap(filename: str, urls: list) -> None:
    """Escreve um arquivo sitemap XML com as URLs fornecidas."""
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
    out_path = OUTPUT_ROOT / filename
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] {filename} -> {len(urls)} URLs")


def extract_date_from_filename(filename: str) -> str:
    """Extrai data do nome do arquivo - busca padrao YYYYMMDD no final (antes do .html)."""
    # Busca YYYYMMDD no final do nome (ex: analise-MLB123-20260531.html)
    m = re.search(r"-(\d{4})(\d{2})(\d{2})(?:\.html)?$", filename)
    if m:
        year, month, day = m.group(1), m.group(2), m.group(3)
        # Validar que é uma data razoável
        y, mo, d = int(year), int(month), int(day)
        if 2020 <= y <= 2030 and 1 <= mo <= 12 and 1 <= d <= 31:
            return f"{year}-{month}-{day}"
    # Busca YYYY-MM-DD no nome
    m = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    if m:
        return m.group(1)
    return NOW_DATE


def collect_posts() -> list:
    """Coleta todos os posts individuais de noticias/posts/."""
    posts_dir = OUTPUT_ROOT / "noticias" / "posts"
    urls = []
    if not posts_dir.exists():
        return urls
    for f in sorted(posts_dir.glob("*.html")):
        date = extract_date_from_filename(f.name)
        urls.append({
            "loc": f"{BASE_URL}/noticias/posts/{f.name}",
            "lastmod": date,
            "changefreq": "monthly",
            "priority": "0.8",
        })
    return urls


def collect_ofertas() -> list:
    """Coleta todas as páginas de ofertas/produtos."""
    ofertas_dir = OUTPUT_ROOT / "ofertas"
    urls = []
    if not ofertas_dir.exists():
        return urls
    for html_file in sorted(ofertas_dir.rglob("*.html")):
        rel = html_file.relative_to(OUTPUT_ROOT)
        urls.append({
            "loc": f"{BASE_URL}/{rel}",
            "lastmod": NOW_DATE,
            "changefreq": "daily",
            "priority": "0.7",
        })
    return urls


def collect_produtos_intel() -> list:
    """Coleta páginas de inteligência de produtos (produtos/)."""
    produtos_dir = OUTPUT_ROOT / "produtos"
    urls = []
    if not produtos_dir.exists():
        return urls
    for html_file in sorted(produtos_dir.rglob("*.html")):
        rel = html_file.relative_to(OUTPUT_ROOT)
        urls.append({
            "loc": f"{BASE_URL}/{rel}",
            "lastmod": NOW_DATE,
            "changefreq": "daily",
            "priority": "0.7",
        })
    return urls


def collect_categorias() -> list:
    """Coleta páginas de categorias."""
    cat_dir = OUTPUT_ROOT / "categorias"
    urls = []
    if not cat_dir.exists():
        return urls
    for index_file in sorted(cat_dir.glob("*/index.html")):
        cat_name = index_file.parent.name
        urls.append({
            "loc": f"{BASE_URL}/categorias/{cat_name}/",
            "lastmod": NOW_DATE,
            "changefreq": "daily",
            "priority": "0.8",
        })
    return urls


def collect_guias() -> list:
    """Coleta páginas de guias."""
    guias_dir = OUTPUT_ROOT / "guias"
    urls = []
    if not guias_dir.exists():
        return urls
    for index_file in sorted(guias_dir.glob("*/index.html")):
        guia_name = index_file.parent.name
        urls.append({
            "loc": f"{BASE_URL}/guias/{guia_name}/",
            "lastmod": NOW_DATE,
            "changefreq": "monthly",
            "priority": "0.9",
        })
    return urls


def collect_comparativos() -> list:
    """Coleta páginas de comparativos (A vs B)."""
    comp_dir = OUTPUT_ROOT / "comparar"
    urls = []
    if not comp_dir.exists():
        return urls
    for f in sorted(comp_dir.glob("*.html")):
        urls.append({
            "loc": f"{BASE_URL}/comparar/{f.name}",
            "lastmod": NOW_DATE,
            "changefreq": "weekly",
            "priority": "0.8",
        })
    return urls


def collect_rankings() -> list:
    """Coleta páginas de rankings (Melhores 2026)."""
    rank_dir = OUTPUT_ROOT / "melhores-2026"
    urls = []
    if not rank_dir.exists():
        return urls
    for f in sorted(rank_dir.glob("*.html")):
        urls.append({
            "loc": f"{BASE_URL}/melhores-2026/{f.name}",
            "lastmod": NOW_DATE,
            "changefreq": "daily",
            "priority": "0.9",
        })
    return urls


def collect_static_pages() -> list:
    """Coleta páginas estáticas importantes do site."""
    static_pages = [
        # Páginas principais (alta prioridade)
        {"loc": f"{BASE_URL}/", "changefreq": "hourly", "priority": "1.0"},
        {"loc": f"{BASE_URL}/melhores-ofertas/", "changefreq": "hourly", "priority": "0.9"},
        {"loc": f"{BASE_URL}/ofertas-hoje/", "changefreq": "hourly", "priority": "0.9"},
        {"loc": f"{BASE_URL}/quedas-hoje/", "changefreq": "hourly", "priority": "0.9"},
        {"loc": f"{BASE_URL}/noticias/", "changefreq": "daily", "priority": "0.9"},
        {"loc": f"{BASE_URL}/guias/", "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{BASE_URL}/rankings/", "changefreq": "daily", "priority": "0.8"},
        {"loc": f"{BASE_URL}/comparativos/", "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{BASE_URL}/melhores-2026/", "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{BASE_URL}/black-friday/", "changefreq": "weekly", "priority": "0.7"},
        {"loc": f"{BASE_URL}/cupons/", "changefreq": "daily", "priority": "0.7"},
        # Páginas institucionais
        {"loc": f"{BASE_URL}/sobre/", "changefreq": "monthly", "priority": "0.5"},
        {"loc": f"{BASE_URL}/contato/", "changefreq": "monthly", "priority": "0.5"},
        {"loc": f"{BASE_URL}/privacidade/", "changefreq": "monthly", "priority": "0.4"},
        {"loc": f"{BASE_URL}/termos/", "changefreq": "monthly", "priority": "0.4"},
        {"loc": f"{BASE_URL}/metodologia/", "changefreq": "monthly", "priority": "0.5"},
    ]
    # Adicionar apenas páginas que realmente existem
    result = []
    for page in static_pages:
        path_part = page["loc"].replace(f"{BASE_URL}/", "").rstrip("/")
        if not path_part:
            result.append(dict(page, lastmod=NOW_DATE))
            continue
        page_path = OUTPUT_ROOT / path_part / "index.html"
        if page_path.exists():
            result.append(dict(page, lastmod=NOW_DATE))
    return result


def generate_sitemap_index(sitemaps: list) -> None:
    """Gera o sitemap index principal."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for s in sitemaps:
        lines.append("  <sitemap>")
        lines.append(f"    <loc>{BASE_URL}/{s}</loc>")
        lines.append(f"    <lastmod>{NOW_DATE}</lastmod>")
        lines.append("  </sitemap>")
    lines.append("</sitemapindex>")
    out_path = OUTPUT_ROOT / "sitemap.xml"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] sitemap.xml (index com {len(sitemaps)} sitemaps)")


def main():
    print(f"\n{'='*60}")
    print(f"  Gerador de Sitemaps - Compara Preco")
    print(f"  {NOW_DATETIME}")
    print(f"{'='*60}\n")

    # 1. Sitemap de Postagens (posts individuais + hub)
    post_urls = collect_posts()
    noticias_urls = [
        {"loc": f"{BASE_URL}/noticias/", "changefreq": "daily", "priority": "0.9", "lastmod": NOW_DATE}
    ] + post_urls
    write_sitemap("sitemap-noticias.xml", noticias_urls)

    # 2. Sitemap de Produtos (ofertas + páginas de inteligência)
    ofertas_urls = collect_ofertas()
    produtos_intel_urls = collect_produtos_intel()
    all_produtos = ofertas_urls + produtos_intel_urls
    # Deduplicar por loc
    seen = set()
    unique_produtos = []
    for u in all_produtos:
        if u["loc"] not in seen:
            seen.add(u["loc"])
            unique_produtos.append(u)
    write_sitemap("sitemap-produtos.xml", unique_produtos)

    # 3. Sitemap de Categorias
    cat_urls = collect_categorias()
    write_sitemap("sitemap-categorias.xml", cat_urls)

    # 4. Sitemap de Guias
    guia_urls = collect_guias()
    write_sitemap("sitemap-guias.xml", guia_urls)

    # 5. Sitemap de Páginas Estáticas
    static_urls = collect_static_pages()
    write_sitemap("sitemap-paginas.xml", static_urls)

    # 6. Sitemap de Comparativos
    comp_urls = collect_comparativos()
    write_sitemap("sitemap-comparativos.xml", comp_urls)

    # 7. Sitemap de Rankings
    rank_urls = collect_rankings()
    write_sitemap("sitemap-rankings.xml", rank_urls)

    # 8. Sitemap Index
    all_sitemaps = [
        "sitemap-paginas.xml",
        "sitemap-noticias.xml",
        "sitemap-produtos.xml",
        "sitemap-categorias.xml",
        "sitemap-guias.xml",
        "sitemap-comparativos.xml",
        "sitemap-rankings.xml",
    ]
    generate_sitemap_index(all_sitemaps)

    # Resumo
    total = (len(noticias_urls) + len(unique_produtos) +
             len(cat_urls) + len(guia_urls) + len(static_urls))
    print(f"\n{'='*60}")
    print(f"  RESUMO:")
    print(f"  - Posts/Noticias : {len(noticias_urls)} URLs")
    print(f"  - Produtos       : {len(unique_produtos)} URLs")
    print(f"  - Categorias     : {len(cat_urls)} URLs")
    print(f"  - Guias          : {len(guia_urls)} URLs")
    print(f"  - Paginas        : {len(static_urls)} URLs")
    print(f"  - TOTAL          : {total} URLs indexadas")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
