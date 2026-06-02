import json
import os
from pathlib import Path
from jinja2 import Template
from logger import logger

ROOT = Path(__file__).resolve().parents[1]

def load_products():
    with open(ROOT / "data" / "database" / "all_products.json", 'r') as f:
        return json.load(f)

def build_stats_pages():
    products = load_products()
    
    # 1. Maiores Quedas (Tendências)
    drops = sorted(products, key=lambda x: float(x.get("custom_discount_pct", 0)), reverse=True)[:20]
    
    # 2. Mais Populares (Simulado por cliques/visitas no futuro)
    popular = products[:20] 
    
    stats_data = {
        "top_drops": drops,
        "popular_products": popular,
        "total_tracked": len(products)
    }
    
    template_str = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>{{ title }} — Radar Ninja</title>
        <link rel="stylesheet" href="/assets/css/style.css">
    </head>
    <body>
        <header class="header"><div class="container"><a href="/" class="logo">📊 Radar Ninja</a></div></header>
        <main class="container">
            <h1>{{ title }}</h1>
            <p>Análise em tempo real de {{ total_tracked }} produtos monitorados.</p>
            
            <div class="grid">
                {% for p in products %}
                <div class="card">
                    <span class="badge">{{ p.custom_discount_pct }}% OFF</span>
                    <img src="{{ p.image }}" style="width:100px">
                    <h3>{{ p.name }}</h3>
                    <a href="{{ p.custom_affiliate_url }}" class="btn">Ver Preço</a>
                </div>
                {% endfor %}
            </div>
        </main>
    </body>
    </html>
    """
    template = Template(template_str)
    
    # Gerar páginas
    pages = [
        ("tendencias", "Tendências da Semana", drops),
        ("maiores-quedas", "Maiores Quedas de Preço", drops),
        ("mais-populares", "Produtos Mais Populares", popular)
    ]
    
    for slug, title, prod_list in pages:
        out_dir = ROOT / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(template.render(title=title, products=prod_list, total_tracked=len(products)))
        logger.info(f"Página de estatística gerada: {slug}")

if __name__ == "__main__":
    build_stats_pages()
