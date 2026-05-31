
import json
import os
from jinja2 import Template

# Configurações
DATA_FILE = 'data/products/offers.json'
OUTPUT_DIR = 'comparar'
TEMPLATE_FILE = 'templates/comparison_template.html'

def generate_comparisons():
    if not os.path.exists(DATA_FILE):
        print("Arquivo de dados não encontrado.")
        return

    with open(DATA_FILE, 'r') as f:
        products = json.load(f)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Criar pares de comparação (ex: top 10 produtos da mesma categoria)
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
        <title>{{ p1.name }} vs {{ p2.name }} — Qual o melhor? | Radar de Preços</title>
        <link rel="stylesheet" href="../assets/css/style.css">
        <style>
            .comp-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 40px; }
            .comp-card { background: var(--card); padding: 20px; border-radius: 12px; border: 1px solid var(--border); text-align: center; }
            .vs-badge { background: var(--primary); color: white; padding: 10px; border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; margin: -45px auto 20px; font-weight: 800; }
            .winner { border: 2px solid gold !important; position: relative; }
            .winner::after { content: '🏆 VENCEDOR'; position: absolute; top: -10px; right: -10px; background: gold; color: black; padding: 5px 10px; border-radius: 5px; font-size: 10px; font-weight: 800; }
            table { width: 100%; border-collapse: collapse; margin-top: 30px; }
            th, td { padding: 15px; border-bottom: 1px solid var(--border); text-align: left; }
            th { background: var(--bg); }
        </style>
    </head>
    <body>
        <header class="header"><div class="container"><a href="../" class="logo">📊 Radar de Preços</a></div></header>
        <main class="container">
            <h1 style="text-align:center; margin-top:40px;">{{ p1.name }} <span style="color:var(--primary)">vs</span> {{ p2.name }}</h1>
            <div class="comp-container">
                <div class="comp-card {{ 'winner' if p1.custom_discount_pct > p2.custom_discount_pct else '' }}">
                    <img src="{{ p1.image or p1.thumbnail }}" style="max-width:150px;">
                    <h3>{{ p1.name }}</h3>
                    <div class="price-tag">R$ {{ p1.price }}</div>
                    <a href="{{ p1.custom_affiliate_url or p1.permalink }}" class="btn" style="width:100%">Ver no Mercado Livre</a>
                </div>
                <div class="comp-card {{ 'winner' if p2.custom_discount_pct > p1.custom_discount_pct else '' }}">
                    <img src="{{ p2.image or p2.thumbnail }}" style="max-width:150px;">
                    <h3>{{ p2.name }}</h3>
                    <div class="price-tag">R$ {{ p2.price }}</div>
                    <a href="{{ p2.custom_affiliate_url or p2.permalink }}" class="btn" style="width:100%">Ver no Mercado Livre</a>
                </div>
            </div>
            <table>
                <tr><th>Característica</th><th>{{ p1.name[:20] }}...</th><th>{{ p2.name[:20] }}...</th></tr>
                <tr><td>Preço Atual</td><td>R$ {{ p1.price }}</td><td>R$ {{ p2.price }}</td></tr>
                <tr><td>Desconto</td><td>{{ p1.custom_discount_pct }}%</td><td>{{ p2.custom_discount_pct }}%</td></tr>
                <tr><td>Veredito</td>
                    <td colspan="2" style="text-align:center; font-weight:800; color:var(--primary)">
                        O {{ p1.name if p1.custom_discount_pct > p2.custom_discount_pct else p2.name }} está com um desconto maior hoje!
                    </td>
                </tr>
            </table>
        </main>
    </body>
    </html>
    """
    template = Template(template_str)

    for cat, cat_products in categories.items():
        cat_products.sort(key=lambda x: x.get('custom_discount_pct', 0), reverse=True)
        top_products = cat_products[:5] # Limitar a 5 para não gerar arquivos demais no exemplo
        
        for i in range(len(top_products)):
            for j in range(i + 1, len(top_products)):
                p1 = top_products[i]
                p2 = top_products[j]
                
                # Nome do arquivo amigável para SEO
                slug1 = p1['name'].lower().replace(' ', '-').replace('/', '-')[:20]
                slug2 = p2['name'].lower().replace(' ', '-').replace('/', '-')[:20]
                filename = f"{slug1}-vs-{slug2}.html"
                
                with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
                    f.write(template.render(p1=p1, p2=p2))
                print(f"Gerado: {filename}")

if __name__ == "__main__":
    generate_comparisons()
