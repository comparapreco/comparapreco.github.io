import json
import os
import re
import html
import random
from pathlib import Path
from jinja2 import Template
from logger import logger

ROOT = Path(__file__).resolve().parents[1]
SITE_KEY = os.environ.get("SITE_KEY")
SITE_CATEGORIES = os.environ.get("SITE_CATEGORIES", "").split(",")
PRODUCTS_FILE = ROOT / "data" / "database" / "all_products.json"

OUTPUT_BASE = ROOT
BASE_URL = "https://comparapreco.github.io/"

def money(value):
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "N/A"

def load_products():
    if not PRODUCTS_FILE.exists():
        return []
    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        products = json.load(f)
    return [p for p in products if p.get("status") == "active"]

def generate_comparisons(products):
    logger.info(f"Gerando comparativos avançados para {SITE_KEY or 'main site'}...")
    out_dir = OUTPUT_BASE / "comparar"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Agrupar por categoria
    cats = {}
    for p in products:
        c = p.get("custom_category_slug", "geral")
        if c not in cats: cats[c] = []
        cats[c].append(p)
        
    template_str = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ p1.name }} vs {{ p2.name }} — Qual o melhor? | Radar Ninja</title>
        <link rel="stylesheet" href="../../assets/css/style.css">
        <style>
            .comp-header { text-align: center; margin: 40px 0; }
            .comp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 40px; }
            .product-card { background: var(--card); padding: 25px; border-radius: 16px; border: 1px solid var(--border); text-align: center; transition: transform 0.2s; }
            .product-card:hover { transform: translateY(-5px); }
            .vs-divider { display: flex; align-items: center; justify-content: center; font-weight: 900; color: var(--primary); font-size: 24px; margin: 20px 0; }
            .specs-table { width: 100%; border-collapse: collapse; margin-top: 30px; background: white; border-radius: 12px; overflow: hidden; }
            .specs-table th, .specs-table td { padding: 15px; border-bottom: 1px solid #eee; text-align: left; }
            .specs-table th { background: #f8f9fa; font-weight: 700; }
            .winner-badge { background: #ffd700; color: #000; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 800; margin-bottom: 10px; display: inline-block; }
        </style>
    </head>
    <body>
        <header class="header"><div class="container"><a href="../../" class="logo">📊 Radar Ninja</a></div></header>
        <main class="container">
            <div class="comp-header">
                <h1>{{ p1.name }} <span style="color:var(--primary)">vs</span> {{ p2.name }}</h1>
                <p>Comparativo técnico detalhado e análise de custo-benefício.</p>
            </div>
            
            <div class="comp-grid">
                <div class="product-card">
                    {% if p1.custom_discount_pct > p2.custom_discount_pct %}<span class="winner-badge">🏆 MELHOR DESCONTO</span>{% endif %}
                    <img src="{{ p1.image }}" style="max-width:180px; height:180px; object-fit:contain; margin-bottom:20px;">
                    <h3>{{ p1.name }}</h3>
                    <div class="price-tag" style="font-size:24px; color:var(--primary); margin:15px 0;">{{ money(p1.price) }}</div>
                    <a href="{{ p1.custom_affiliate_url }}" class="btn" style="width:100%">Ver no Mercado Livre</a>
                </div>
                <div class="product-card">
                    {% if p2.custom_discount_pct > p1.custom_discount_pct %}<span class="winner-badge">🏆 MELHOR DESCONTO</span>{% endif %}
                    <img src="{{ p2.image }}" style="max-width:180px; height:180px; object-fit:contain; margin-bottom:20px;">
                    <h3>{{ p2.name }}</h3>
                    <div class="price-tag" style="font-size:24px; color:var(--primary); margin:15px 0;">{{ money(p2.price) }}</div>
                    <a href="{{ p2.custom_affiliate_url }}" class="btn" style="width:100%">Ver no Mercado Livre</a>
                </div>
            </div>

            <table class="specs-table">
                <thead>
                    <tr>
                        <th>Característica</th>
                        <th>{{ p1.name[:30] }}...</th>
                        <th>{{ p2.name[:30] }}...</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Preço Atual</td>
                        <td>{{ money(p1.price) }}</td>
                        <td>{{ money(p2.price) }}</td>
                    </tr>
                    <tr>
                        <td>Desconto Real</td>
                        <td style="color:var(--success); font-weight:700;">{{ p1.custom_discount_pct }}% OFF</td>
                        <td style="color:var(--success); font-weight:700;">{{ p2.custom_discount_pct }}% OFF</td>
                    </tr>
                    <tr>
                        <td>Veredito Radar Ninja</td>
                        <td colspan="2" style="text-align:center; font-weight:800; background:#fff9e6;">
                            O {{ p1.name if p1.custom_discount_pct > p2.custom_discount_pct else p2.name }} é a melhor escolha hoje pelo desconto agressivo!
                        </td>
                    </tr>
                </tbody>
            </table>
        </main>
    </body>
    </html>
    """
    template = Template(template_str)
    for cat, items in cats.items():
        items.sort(key=lambda x: float(x.get("custom_discount_pct", 0)), reverse=True)
        top = items[:15] # Aumentado para 15 para o portal gigante
        for i in range(len(top)):
            for j in range(i+1, len(top)):
                p1, p2 = top[i], top[j]
                slug1 = re.sub(r'[^a-z0-9]+', '-', p1['name'].lower())[:30].strip('-')
                slug2 = re.sub(r'[^a-z0-9]+', '-', p2['name'].lower())[:30].strip('-')
                fname = f"{slug1}-vs-{slug2}.html"
                (out_dir / fname).write_text(template.render(p1=p1, p2=p2, money=money))

def generate_rankings(products):
    logger.info(f"Gerando rankings validados para {SITE_KEY or 'main site'}...")
    from generate_rankings import generate_rankings as generate_validated_rankings
    generate_validated_rankings()

def main():
    products = load_products()
    if not products:
        logger.warning("Nenhum produto encontrado para SEO Programático.")
        return
    generate_comparisons(products)
    generate_rankings(products)

if __name__ == "__main__":
    main()
