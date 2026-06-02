import json
import os
from pathlib import Path
from jinja2 import Template
from logger import logger

ROOT = Path(__file__).resolve().parents[1]

def build_daily_deals():
    with open(ROOT / "data" / "database" / "all_products.json", 'r') as f:
        products = json.load(f)
    
    # Ofertas do dia: Descontos > 20%
    deals = [p for p in products if float(p.get("custom_discount_pct", 0)) > 20]
    deals.sort(key=lambda x: float(x.get("custom_discount_pct", 0)), reverse=True)
    
    template_str = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Ofertas do Dia — Radar Ninja</title>
        <link rel="stylesheet" href="/assets/css/style.css">
    </head>
    <body>
        <header class="header"><div class="container"><a href="/" class="logo">📊 Radar Ninja</a></div></header>
        <main class="container">
            <div style="background:var(--primary); color:white; padding:40px; border-radius:16px; margin-bottom:40px; text-align:center;">
                <h1>⚡ Ofertas do Dia</h1>
                <p>As melhores oportunidades encontradas pelos nossos ninjas nas últimas 24 horas.</p>
            </div>
            <div class="grid">
                {% for p in deals %}
                <div class="card">
                    <div class="price-drop">-{{ p.custom_discount_pct }}%</div>
                    <img src="{{ p.image }}" style="width:120px">
                    <h3>{{ p.name }}</h3>
                    <a href="{{ p.custom_affiliate_url }}" class="btn">Aproveitar Agora</a>
                </div>
                {% endfor %}
            </div>
        </main>
    </body>
    </html>
    """
    out_dir = ROOT / "ofertas-hoje"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(Template(template_str).render(deals=deals[:50]))
    logger.info("Página de Ofertas do Dia gerada com sucesso.")

if __name__ == "__main__":
    build_daily_deals()
