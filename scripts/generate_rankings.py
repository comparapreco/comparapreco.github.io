
import json
import os
from jinja2 import Template

# Configurações
DATA_FILE = 'data/products/offers.json'
OUTPUT_DIR = 'melhores-2026'

def generate_rankings():
    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, 'r') as f:
        products = json.load(f)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    categories = {}
    for p in products:
        cat = p.get('custom_category_slug', 'outros')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(p)

    template_str = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Melhores {{ category_name }} de 2026 — Ranking Atualizado | Radar de Preços</title>
        <link rel="stylesheet" href="../assets/css/style.css">
        <style>
            .rank-item { display: flex; align-items: center; gap: 20px; background: var(--card); padding: 20px; border-radius: 12px; border: 1px solid var(--border); margin-bottom: 20px; }
            .rank-number { font-size: 40px; font-weight: 900; color: var(--primary); opacity: 0.3; min-width: 60px; }
            .rank-img { width: 100px; height: 100px; object-fit: contain; }
            .rank-info { flex: 1; }
        </style>
    </head>
    <body>
        <header class="header"><div class="container"><a href="../" class="logo">📊 Radar de Preços</a></div></header>
        <main class="container">
            <h1 style="margin: 40px 0;">🏆 Melhores {{ category_name }} de 2026</h1>
            <p>Ranking baseado em custo-benefício, desconto real e avaliações no Mercado Livre.</p>
            
            {% for p in products %}
            <div class="rank-item">
                <div class="rank-number">#{{ loop.index }}</div>
                <img src="{{ p.image or p.thumbnail }}" class="rank-img">
                <div class="rank-info">
                    <h3>{{ p.name }}</h3>
                    <div class="price-tag">R$ {{ p.price }} <span style="font-size:14px; color:var(--success)">({{ p.custom_discount_pct }}% OFF)</span></div>
                    <a href="{{ p.custom_affiliate_url or p.permalink }}" class="btn">Ver Melhor Preço</a>
                </div>
            </div>
            {% endfor %}
        </main>
    </body>
    </html>
    """
    template = Template(template_str)

    for cat, cat_products in categories.items():
        cat_products.sort(key=lambda x: x.get('custom_discount_pct', 0), reverse=True)
        top_10 = cat_products[:10]
        
        filename = f"melhores-{cat}-2026.html"
        with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
            f.write(template.render(category_name=cat.capitalize(), products=top_10))
        print(f"Gerado Ranking: {filename}")

if __name__ == "__main__":
    generate_rankings()
