import json
import os
from pathlib import Path
from typing import Dict, List

from jinja2 import Template

from quality_utils import as_float, clean_product_name, escape_attr, money, normalize_product, product_signature, slugify
from schema_utils import BASE_URL, itemlist_schema, jsonld, product_image, product_offer_url, product_page_url
from validate_products import validate_product

DATA_FILE = Path('data/products/offers.json')
FALLBACK_DATA_FILE = Path('data/database/all_products.json')
OUTPUT_DIR = Path('melhores-2026')


def _load_products() -> List[Dict]:
    products: List[Dict] = []
    for data_file in [DATA_FILE, FALLBACK_DATA_FILE, Path('data/new_offers.json')]:
        if not data_file.exists():
            continue
        with data_file.open('r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            products.extend([p for p in data if isinstance(p, dict)])
    return products


def _valid_unique_products(products: List[Dict]) -> List[Dict]:
    valid: List[Dict] = []
    seen = set()
    for raw in products:
        if not isinstance(raw, dict):
            continue
        product = normalize_product(raw)
        ok, _reason = validate_product(product, mutate=False, strict_links=False)
        if not ok:
            continue
        image = product_image(product)
        offer_url = product_offer_url(product)
        if not image or not offer_url or as_float(product.get('price')) <= 0:
            continue
        pid = str(product.get('id') or '').strip()
        key = pid or product_signature(product)
        if key in seen:
            continue
        seen.add(key)
        product['image'] = image
        product['custom_affiliate_url'] = offer_url
        product['product_page_url'] = product_page_url(product)
        product['display_name'] = clean_product_name(product.get('name') or product.get('title'), 105)
        product['display_price'] = money(product.get('price'))
        product['category_label'] = str(product.get('custom_category_slug') or 'outros').replace('-', ' ').title()
        valid.append(product)
    return valid


def _score(product: Dict) -> float:
    return as_float(product.get('custom_discount_pct')) * 1000 + max(0, 100000 - as_float(product.get('price')))


RANKING_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ title }}</title>
  <meta name="description" content="{{ description }}">
  <link rel="canonical" href="{{ canonical_url }}">
  <link rel="stylesheet" href="../assets/css/style.css">
  <script type="application/ld+json">
{{ schema_json }}
  </script>
  <style>
    .rank-item { display: flex; align-items: center; gap: 20px; background: var(--card); padding: 20px; border-radius: 12px; border: 1px solid var(--border); margin-bottom: 20px; }
    .rank-number { font-size: 40px; font-weight: 900; color: var(--primary); opacity: 0.3; min-width: 60px; }
    .rank-img { width: 120px; height: 120px; object-fit: contain; background: #fff; border-radius: 10px; }
    .rank-info { flex: 1; }
    .rank-meta { color: var(--text-light); font-size: 0.95rem; margin-top: 8px; }
  </style>
</head>
<body>
  <header class="header"><div class="container"><a href="../" class="logo">Compara Preço</a></div></header>
  <main class="container">
    <h1 style="margin: 40px 0 12px;">{{ heading }}</h1>
    <p>{{ intro }}</p>
    {% for p in products %}
    <article class="rank-item">
      <div class="rank-number">#{{ loop.index }}</div>
      <a href="{{ p.product_page_url }}"><img src="{{ p.image }}" alt="{{ p.display_name }}" class="rank-img" loading="lazy" width="120" height="120"></a>
      <div class="rank-info">
        <h2 style="font-size:1.15rem; margin:0 0 8px;"><a href="{{ p.product_page_url }}" style="color:inherit;text-decoration:none;">{{ p.display_name }}</a></h2>
        <div class="price-tag">{{ p.display_price }} <span style="font-size:14px; color:var(--success)">{{ p.custom_discount_pct|default(0) }}% OFF</span></div>
        <div class="rank-meta">Categoria: {{ p.category_label }}. Dados validados antes da publicação.</div>
        <a href="{{ p.product_page_url }}" class="btn">Ver análise e melhor preço</a>
      </div>
    </article>
    {% endfor %}
  </main>
</body>
</html>
""")


INDEX_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Melhores Produtos de 2026 — Rankings por categoria | Compara Preço</title>
  <meta name="description" content="Rankings de melhores produtos de 2026 por categoria, com preços, imagens, links e dados estruturados validados automaticamente.">
  <link rel="canonical" href="{{ canonical_url }}">
  <link rel="stylesheet" href="../assets/css/style.css">
  <script type="application/ld+json">
{{ schema_json }}
  </script>
  <style>.category-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px}.cat-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:22px;text-decoration:none;color:inherit}.cat-card strong{display:block;font-size:1.1rem;margin-bottom:8px}</style>
</head>
<body>
  <header class="header"><div class="container"><a href="../" class="logo">Compara Preço</a></div></header>
  <main class="container">
    <h1 style="margin: 40px 0 12px;">Melhores produtos de 2026</h1>
    <p>Esta página organiza os rankings por categoria. O robô bloqueia produtos sem preço, imagem, link válido ou dados estruturados consistentes antes da publicação.</p>
    <section class="category-grid">
      {% for cat in categories %}
      <a class="cat-card" href="{{ cat.file }}"><strong>{{ cat.name }}</strong><span>{{ cat.count }} produtos validados no ranking.</span></a>
      {% endfor %}
    </section>
  </main>
</body>
</html>
""")


def _render_page(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding='utf-8')


def generate_rankings() -> None:
    products = _valid_unique_products(_load_products())
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    categories: Dict[str, List[Dict]] = {}
    for p in products:
        cat = p.get('custom_category_slug') or 'outros'
        categories.setdefault(cat, []).append(p)

    index_cards = []
    global_top: List[Dict] = []
    for cat, cat_products in sorted(categories.items()):
        cat_products.sort(key=_score, reverse=True)
        top_10 = cat_products[:10]
        if not top_10:
            continue
        category_name = cat.replace('-', ' ').title()
        filename = f"melhores-{slugify(cat, 80)}-2026.html"
        canonical_url = f"{BASE_URL}melhores-2026/{filename}"
        title = f"Melhores {category_name} de 2026 — Ranking Atualizado | Compara Preço"
        description = f"Ranking de melhores produtos de {category_name} em 2026 com preço, imagem, disponibilidade, link e Schema.org validados automaticamente."
        schema_json = jsonld(itemlist_schema(top_10, canonical_url, title))
        html = RANKING_TEMPLATE.render(
            title=escape_attr(title),
            description=escape_attr(description),
            canonical_url=canonical_url,
            heading=f"Melhores {category_name} de 2026",
            intro=f"Ranking baseado em produtos com preço positivo, imagem válida, link rastreável e dados estruturados Product/Offer consistentes.",
            products=top_10,
            schema_json=schema_json,
        )
        _render_page(OUTPUT_DIR / filename, html)
        index_cards.append({'name': category_name, 'file': filename, 'count': len(top_10)})
        global_top.extend(top_10[:2])
        print(f"Gerado ranking validado: {filename}")

    global_top = sorted(global_top, key=_score, reverse=True)[:10]
    index_schema = jsonld(itemlist_schema(global_top, f"{BASE_URL}melhores-2026/", "Melhores Produtos de 2026"))
    index_html = INDEX_TEMPLATE.render(canonical_url=f"{BASE_URL}melhores-2026/", schema_json=index_schema, categories=index_cards)
    _render_page(OUTPUT_DIR / 'index.html', index_html)
    print("Gerado índice validado: index.html")


if __name__ == "__main__":
    generate_rankings()
