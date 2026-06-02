import json
import os
import re
from pathlib import Path
from jinja2 import Template
from logger import logger

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "database" / "all_products.json"
CONFIG_FILE = ROOT / "data" / "portal_config.json"

def money(value):
    try: return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "N/A"

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f: products = json.load(f)
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f: config = json.load(f)
    return products, config

def get_brands(products):
    brands = {}
    for p in products:
        brand = p.get("brand")
        if not brand:
            # Tentar extrair do nome se não houver campo brand
            name = p.get("name", "").split()[0]
            brand = name if len(name) > 2 else "Outros"
        brand = brand.title()
        if brand not in brands: brands[brand] = []
        brands[brand].append(p)
    return brands

def build_hubs():
    products, config = load_data()
    brands = get_brands(products)
    
    hub_template = """
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
            <nav class="breadcrumb"><a href="/">Home</a> / {{ title }}</nav>
            <h1>{{ title }}</h1>
            <p>{{ description }}</p>
            
            <section class="hub-section">
                <h2>🏆 Melhores Produtos</h2>
                <div class="grid">
                    {% for p in top_products %}
                    <div class="card">
                        <img src="{{ p.image }}" style="width:100px">
                        <h3>{{ p.name }}</h3>
                        <p class="price">{{ money(p.price) }}</p>
                        <a href="{{ p.custom_affiliate_url }}" class="btn">Ver Oferta</a>
                    </div>
                    {% endfor %}
                </div>
            </section>

            <section class="hub-section">
                <h2>🔄 Comparativos Populares</h2>
                <ul>
                    {% for comp in comps %}
                    <li><a href="/comparar/{{ comp.file }}">{{ comp.name }}</a></li>
                    {% endfor %}
                </ul>
            </section>
        </main>
    </body>
    </html>
    """
    template = Template(hub_template)
    
    # Gerar Hubs de Categorias Temáticas
    for theme_key, theme_data in config["themes"].items():
        logger.info(f"Gerando Hub: {theme_data['name']}")
        theme_products = [p for p in products if p.get("custom_category_slug") in theme_data["categories"]]
        theme_products.sort(key=lambda x: float(x.get("custom_discount_pct", 0)), reverse=True)
        
        out_dir = ROOT / "categorias" / theme_key
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Simular busca de comparativos relacionados
        comps = [] # Lógica para buscar arquivos em /comparar que batam com as categorias
        
        content = template.render(
            title=theme_data["name"],
            description=f"Central de ofertas, comparativos e guias para {theme_data['name']}.",
            top_products=theme_products[:12],
            comps=comps,
            money=money
        )
        (out_dir / "index.html").write_text(content)

    # Gerar Hubs de Marcas
    popular_brands = ["Samsung", "Xiaomi", "LG", "Mondial", "Philco", "Electrolux", "Brastemp", "Consul", "Motorola", "Lenovo"]
    for brand_name in popular_brands:
        if brand_name in brands:
            logger.info(f"Gerando Hub de Marca: {brand_name}")
            brand_products = brands[brand_name]
            brand_products.sort(key=lambda x: float(x.get("custom_discount_pct", 0)), reverse=True)
            
            out_dir = ROOT / "marcas" / brand_name.lower()
            out_dir.mkdir(parents=True, exist_ok=True)
            
            content = template.render(
                title=f"Produtos {brand_name}",
                description=f"Tudo sobre {brand_name}: melhores preços, comparativos e histórico.",
                top_products=brand_products[:12],
                comps=[],
                money=money
            )
            (out_dir / "index.html").write_text(content)

if __name__ == "__main__":
    build_hubs()
