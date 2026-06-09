#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today().isoformat()
BASE_URL = 'https://comparapreco.github.io'

PRODUCT_FILES = [
    ROOT / 'data' / 'database' / 'all_products.json',
    ROOT / 'data' / 'curated_products.json',
    ROOT / 'data' / 'validated_products.json',
    ROOT / 'data' / 'affiliate_products.json',
]

PAGES = [
    {
        'slug': 'melhores-celulares-samsung',
        'title': 'Melhores Celulares Samsung em Promoção',
        'h1': 'Melhores celulares Samsung em promoção hoje',
        'icon': '📱',
        'description': 'Veja celulares Samsung e modelos Galaxy com descontos verificados, preço monitorado e links diretos para compra segura.',
        'intro': 'Esta página reúne smartphones Samsung e produtos Galaxy encontrados na base do Compara Preço. A seleção prioriza itens com maior desconto, preço claro e link de compra rastreável, criando uma página forte para quem procura Samsung com economia real.',
        'keywords': ['samsung', 'galaxy', 'celular', 'smartphone'],
        'must_any': ['samsung', 'galaxy'],
        'guide': [
            'Compare memória RAM e armazenamento antes de decidir, principalmente se você usa muitos aplicativos.',
            'Priorize modelos com 5G e boa política de atualização quando a diferença de preço for pequena.',
            'Verifique se o desconto é relevante em relação ao preço original informado e ao histórico de ofertas do site.',
        ],
    },
    {
        'slug': 'melhores-notebooks-ate-3000',
        'title': 'Melhores Notebooks até R$ 3.000',
        'h1': 'Melhores notebooks até R$ 3.000 em oferta',
        'icon': '💻',
        'description': 'Lista de notebooks até R$ 3.000 com curadoria do Compara Preço para estudar, trabalhar e comprar gastando menos.',
        'intro': 'A faixa até R$ 3.000 é uma das mais buscadas por quem precisa de notebook para estudo, trabalho remoto e tarefas do dia a dia. Esta página centraliza ofertas elegíveis e ajuda o Google a encontrar uma rota clara para esse tipo de busca.',
        'keywords': ['notebook', 'laptop', 'chromebook'],
        'max_price': 3000,
        'guide': [
            'Dê preferência a SSD, pois ele deixa o sistema mais rápido que HD tradicional.',
            'Para multitarefa, 8 GB de RAM costuma ser o mínimo recomendável nessa faixa de preço.',
            'Observe tela, peso e autonomia se o notebook será usado fora de casa.',
        ],
    },
    {
        'slug': 'melhores-tvs-4k',
        'title': 'Melhores TVs 4K em Promoção',
        'h1': 'Melhores TVs 4K em promoção hoje',
        'icon': '📺',
        'description': 'Compare Smart TVs 4K e UHD com desconto, organizadas para facilitar a escolha por tamanho, marca e economia.',
        'intro': 'Esta página agrupa Smart TVs, modelos 4K e TVs UHD com descontos relevantes. O objetivo é criar uma página de categoria forte, com links normais em HTML para produtos e marcas, melhorando descoberta, navegação e intenção comercial.',
        'keywords': ['tv', 'smart tv', '4k', 'uhd'],
        'guide': [
            'Confira se a TV tem o sistema de apps que você usa, como streaming e recursos de espelhamento.',
            'Avalie tamanho e distância do sofá; telas maiores exigem mais espaço para conforto visual.',
            'Compare conectividade HDMI, Wi-Fi e recursos HDR antes de escolher pelo menor preço.',
        ],
    },
    {
        'slug': 'melhores-fones-bluetooth',
        'title': 'Melhores Fones Bluetooth em Promoção',
        'h1': 'Melhores fones Bluetooth em promoção hoje',
        'icon': '🎧',
        'description': 'Encontre fones Bluetooth, earbuds e headphones com descontos verificados e links diretos para ofertas atualizadas.',
        'intro': 'Fones Bluetooth são produtos de alta intenção de compra, com grande variação de preço e qualidade. Esta página concentra ofertas relevantes e cria uma rota de navegação clara para usuários e buscadores.',
        'keywords': ['fone', 'bluetooth', 'buds', 'earbuds', 'headphone', 'airpods'],
        'guide': [
            'Observe autonomia de bateria e tipo de carregamento antes de comprar.',
            'Se você usa em chamadas, confira microfone, cancelamento de ruído e conforto.',
            'Compare modelos intra-auriculares, headphones e earbuds conforme seu uso principal.',
        ],
    },
]


def load_products() -> list[dict[str, Any]]:
    products: list[dict[str, Any]] = []
    for path in PRODUCT_FILES:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(data, list):
            products.extend(x for x in data if isinstance(x, dict))
        elif isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list):
                    products.extend(x for x in value if isinstance(x, dict))
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for product in products:
        key = str(product.get('id') or product.get('custom_affiliate_url') or product.get('permalink') or product.get('title') or product.get('name'))
        if key and key != 'None' and key not in seen:
            seen.add(key)
            unique.append(product)
    return unique


def product_text(product: dict[str, Any]) -> str:
    return ' '.join(str(product.get(k, '')) for k in ('name', 'title', 'custom_category_slug', 'category')).lower()


def price(product: dict[str, Any]) -> float:
    for key in ('price', 'current_price', 'sale_price'):
        try:
            return float(product.get(key) or 0)
        except (TypeError, ValueError):
            pass
    return 0.0


def discount(product: dict[str, Any]) -> int:
    value = product.get('custom_discount_pct') or product.get('discount') or product.get('discount_pct') or 0
    try:
        return int(float(value))
    except (TypeError, ValueError):
        original = product.get('originalPrice') or product.get('original_price') or 0
        current = price(product)
        try:
            if original and current:
                return max(0, round((float(original) - current) * 100 / float(original)))
        except (TypeError, ValueError, ZeroDivisionError):
            return 0
    return 0


def affiliate_url(product: dict[str, Any]) -> str:
    url = product.get('custom_affiliate_url') or product.get('affiliate_url') or product.get('permalink') or '#'
    if 'mercadolivre.com' in url and 'matt_tool=' not in url:
        sep = '&' if '?' in url else '?'
        url = f'{url}{sep}matt_tool=60566305'
    return str(url)


def select_products(products: list[dict[str, Any]], page: dict[str, Any]) -> list[dict[str, Any]]:
    keywords = [k.lower() for k in page['keywords']]
    chosen: list[dict[str, Any]] = []
    for product in products:
        text = product_text(product)
        if not any(keyword in text for keyword in keywords):
            continue
        if page.get('must_any') and not any(keyword in text for keyword in page['must_any']):
            continue
        if page.get('max_price') and price(product) > float(page['max_price']):
            continue
        chosen.append(product)

    chosen.sort(key=lambda p: (discount(p), -price(p)), reverse=True)
    return chosen[:24]


def money(value: float) -> str:
    if not value:
        return 'Preço sob consulta'
    return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def product_card(product: dict[str, Any]) -> str:
    import sys
    sys.path.append(str(ROOT / 'scripts'))
    from quality_utils import clean_product_name, slugify, normalize_product

    product = normalize_product(product)
    p_name = clean_product_name(product.get('name') or product.get('title') or 'Produto em oferta')
    title = html.escape(p_name)
    p_slug = slugify(p_name)
    p_cat = product.get('custom_category_slug', 'outros')
    p_id = product.get('id', '0')

    local_offer = ROOT / 'ofertas' / p_cat / f'{p_slug}-{p_id}.html'
    if not local_offer.exists():
        return ''

    url = f"../../ofertas/{p_cat}/{p_slug}-{p_id}.html"

    img = html.escape(str(product.get('image') or product.get('thumbnail') or ''), quote=True)
    current = money(price(product))
    disc = discount(product)
    image_html = f'<img src="{img}" alt="{title}" loading="lazy"/>' if img else '<div class="no-image">Oferta</div>'
    badge = f'<span class="discount-badge">-{disc}%</span>' if disc else '<span class="discount-badge neutral">Oferta</span>'
    return f'''<article class="strategic-product-card">
      <a href="{url}" title="{title}">
        <div class="product-image-wrap">{image_html}{badge}</div>
        <h3>{title}</h3>
        <p class="price">{current}</p>
        <span class="cta">Ver Detalhes da Oferta</span>
      </a>
    </article>'''


def build_page(page: dict[str, Any], products: list[dict[str, Any]]) -> str:
    cards = '\n'.join(product_card(product) for product in products)
    related = ''.join(
        f'<a href="../{p["slug"]}/">{p["icon"]} {html.escape(p["title"])}</a>'
        for p in PAGES if p['slug'] != page['slug']
    )
    guide_items = ''.join(f'<li>{html.escape(item)}</li>' for item in page['guide'])
    count = len(products)
    canonical = f'{BASE_URL}/melhores-ofertas/{page["slug"]}/'
    title = html.escape(page['title'])
    desc = html.escape(page['description'])
    h1 = html.escape(page['h1'])
    intro = html.escape(page['intro'])
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title} | Compara Preço</title>
  <meta name="description" content="{desc}"/>
  <link rel="canonical" href="{canonical}"/>
  <link rel="stylesheet" href="../../assets/css/style.css"/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet"/>
  <meta name="google-adsense-account" content="ca-pub-4896859041377751"/>
  <style>
    .strategic-hero {{ background: linear-gradient(135deg, #111827 0%, #7c3aed 100%); color: #fff; padding: 56px 0 44px; margin-bottom: 34px; }}
    .breadcrumb {{ font-size: 13px; opacity: .86; margin-bottom: 14px; }}
    .breadcrumb a {{ color: #fff; text-decoration: none; }}
    .strategic-hero h1 {{ font-size: clamp(2rem, 4vw, 3rem); margin: 0 0 12px; line-height: 1.1; }}
    .strategic-hero p {{ max-width: 820px; font-size: 1.05rem; line-height: 1.7; opacity: .94; }}
    .quick-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin: 22px 0 34px; }}
    .quick-stat {{ background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 18px; }}
    .quick-stat strong {{ display:block; font-size:1.65rem; color: var(--primary); }}
    .editorial-box {{ background: var(--card); border: 1px solid var(--border); border-radius: 18px; padding: 24px; margin-bottom: 34px; }}
    .editorial-box h2 {{ margin-top: 0; }}
    .editorial-box li {{ margin: 8px 0; line-height: 1.55; }}
    .strategic-products-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 20px; margin: 24px 0 42px; }}
    .strategic-product-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 18px; overflow: hidden; transition: transform .2s, box-shadow .2s; }}
    .strategic-product-card:hover {{ transform: translateY(-4px); box-shadow: 0 14px 34px rgba(0,0,0,.12); }}
    .strategic-product-card a {{ color: inherit; text-decoration: none; display:block; height:100%; }}
    .product-image-wrap {{ position: relative; aspect-ratio: 1/1; background:#f8fafc; display:flex; align-items:center; justify-content:center; }}
    .product-image-wrap img {{ width:100%; height:100%; object-fit: contain; padding: 14px; }}
    .discount-badge {{ position:absolute; top:12px; left:12px; background:#dc2626; color:#fff; font-weight:800; border-radius:999px; padding:6px 10px; font-size:13px; }}
    .discount-badge.neutral {{ background:#7c3aed; }}
    .strategic-product-card h3 {{ font-size: .98rem; line-height: 1.35; min-height: 54px; margin: 16px 16px 10px; }}
    .price {{ color: var(--primary); font-size: 1.15rem; font-weight: 900; margin: 0 16px 14px; }}
    .cta {{ display:block; margin: 0 16px 18px; color: var(--primary); font-weight:800; font-size:.9rem; }}
    .related-links {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap:14px; margin-bottom:40px; }}
    .related-links a {{ background: var(--card); border:1px solid var(--border); border-radius:14px; padding:16px; text-decoration:none; color:inherit; font-weight:800; }}
  </style>
</head>
<body>
  <header class="header">
    <div class="container header-inner">
      <a href="../../" style="font-weight:900;text-decoration:none;color:inherit;">Compara Preço</a>
      <nav class="nav-links">
        <a href="../../ofertas-hoje/">Ofertas</a>
        <a href="../../aprender/">Aprender</a>
        <a href="../../melhores-ofertas/">Melhores ofertas</a>
      </nav>
    </div>
  </header>
  <section class="strategic-hero">
    <div class="container">
      <div class="breadcrumb"><a href="../../">Início</a> › <a href="../">Melhores ofertas</a> › {title}</div>
      <h1>{page['icon']} {h1}</h1>
      <p>{intro}</p>
    </div>
  </section>
  <main class="container">
    <section class="quick-stats" aria-label="Resumo da página">
      <div class="quick-stat"><strong>{count}</strong><span>ofertas selecionadas</span></div>
      <div class="quick-stat"><strong>HTML</strong><span>links rastreáveis pelo Google</span></div>
      <div class="quick-stat"><strong>{TODAY}</strong><span>última atualização</span></div>
    </section>
    <section class="editorial-box">
      <h2>Como escolher nesta categoria</h2>
      <p>{desc}</p>
      <ul>{guide_items}</ul>
    </section>
    <section>
      <h2>Ofertas selecionadas</h2>
      <div class="strategic-products-grid">{cards}</div>
    </section>
    <section>
      <h2>Outras categorias estratégicas</h2>
      <div class="related-links">{related}</div>
    </section>
  </main>
  <footer class="footer">
    <div class="container">
      <p>© 2026 Compara Preço — Inteligência em compras.</p>
      <div class="footer-links">
        <a href="../../sobre/">Sobre</a>
        <a href="../../privacidade/">Privacidade</a>
        <a href="../../termos/">Termos</a>
      </div>
    </div>
  </footer>
</body>
</html>
'''


def update_homepage() -> None:
    path = ROOT / 'index.html'
    content = path.read_text(encoding='utf-8')
    links = '\n'.join(
        f'        <a class="cat-card" href="/melhores-ofertas/{p["slug"]}/">{p["icon"]} {html.escape(p["title"])}</a>'
        for p in PAGES
    )
    section = f'''\n<section class="section" id="categorias-estrategicas">\n  <h2>🎯 Guias estratégicos de compra</h2>\n  <p style="color: var(--text-light); margin-bottom: 18px;">Páginas fortes com links HTML diretos para ajudar usuários e buscadores a encontrar as ofertas mais importantes.</p>\n  <div class="categories-scroll">\n{links}\n  </div>\n</section>\n'''
    if 'id="categorias-estrategicas"' in content:
        content = re.sub(r'\n<section class="section" id="categorias-estrategicas">.*?</section>\n', section, content, flags=re.S)
    else:
        content = content.replace('<section class="section">\n<h2>📚 Artigos Mais Recentes</h2>', section + '\n<section class="section">\n<h2>📚 Artigos Mais Recentes</h2>')
    path.write_text(content, encoding='utf-8')


def update_melhores_index() -> None:
    path = ROOT / 'melhores-ofertas' / 'index.html'
    content = path.read_text(encoding='utf-8')
    cards = '\n'.join(
        f'''<a class="brand-hub-card" href="{p['slug']}/">
<div class="brand-hub-icon">{p['icon']}</div>
<div class="brand-hub-name">{html.escape(p['title'])}</div>
<div class="brand-hub-desc">{html.escape(p['description'][:82])}...</div>
</a>'''
        for p in PAGES
    )
    block = f'''\n<h2 class="section-title">Categorias Estratégicas</h2>\n<div class="brands-grid strategic-category-grid">\n{cards}\n</div>\n'''
    if 'Categorias Estratégicas' in content:
        content = re.sub(r'\n<h2 class="section-title">Categorias Estratégicas</h2>.*?</div>\n(?=</main>)', block, content, flags=re.S)
    else:
        content = content.replace('</main>', block + '</main>')
    path.write_text(content, encoding='utf-8')


def update_sitemap() -> None:
    path = ROOT / 'sitemap-rankings.xml'
    content = path.read_text(encoding='utf-8')
    additions = []
    for page in PAGES:
        loc = f'{BASE_URL}/melhores-ofertas/{page["slug"]}/'
        if loc in content:
            continue
        additions.append(f'''  <url>
    <loc>{loc}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>''')
    if additions:
        content = content.replace('</urlset>', '\n'.join(additions) + '\n</urlset>')
        path.write_text(content, encoding='utf-8')


def main() -> None:
    products = load_products()
    report = []
    for page in PAGES:
        selected = select_products(products, page)
        target = ROOT / 'melhores-ofertas' / page['slug']
        target.mkdir(parents=True, exist_ok=True)
        (target / 'index.html').write_text(build_page(page, selected), encoding='utf-8')
        report.append({'slug': page['slug'], 'products': len(selected), 'url': f'/melhores-ofertas/{page["slug"]}/'})
    update_homepage()
    update_melhores_index()
    update_sitemap()
    (ROOT / 'RELATORIO_CATEGORIAS_ESTRATEGICAS.md').write_text(
        '# Relatório de categorias estratégicas\n\n' +
        f'Atualização executada em {TODAY}. Foram criadas páginas estratégicas em HTML estático, com links internos na homepage, no hub de melhores ofertas e no sitemap de rankings.\n\n' +
        '| Página | Produtos vinculados | URL |\n|---|---:|---|\n' +
        ''.join(f'| {r["slug"]} | {r["products"]} | `{r["url"]}` |\n' for r in report),
        encoding='utf-8'
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
