import os
import json
import re
from datetime import datetime
from typing import Any, Dict, List
from logger import logger
import random

BASE_URL = "https://comparapreco.github.io/"

def generate_product_specs(product: Dict[str, Any]) -> Dict[str, str]:
    specs = {
        "Modelo": product.get("name", "Produto"),
        "Categoria": product.get("custom_category_slug", "Geral").replace("-", " ").title(),
        "Preço Atual": f"R$ {product.get('price', 0):.2f}",
        "Preço Original": f"R$ {product.get('originalPrice', 0):.2f}",
        "Desconto": f"{product.get('custom_discount_pct', 0)}%",
    }
    name = product.get("name", "").lower()
    if "gb" in name:
        match = re.search(r'(\d+gb)', name)
        if match: specs["Armazenamento"] = match.group(1).upper()
    if "polegadas" in name or '"' in name:
        match = re.search(r'(\d+)(\s?polegadas|\")', name)
        if match: specs["Tela"] = match.group(1) + " polegadas"
    return specs

def generate_pros_cons(product: Dict[str, Any]) -> Dict[str, List[str]]:
    category = product.get("custom_category_slug", "geral")
    pros = ["Excelente custo-benefício com desconto real.", "Vendedor com boa reputação no marketplace."]
    cons = ["Estoque limitado devido à alta demanda.", "Preço pode sofrer alteração a qualquer momento."]
    
    if category == "celulares":
        pros.extend(["Tecnologia de ponta para multitarefa.", "Câmera otimizada para redes sociais."])
    elif category == "tv-e-video":
        pros.extend(["Qualidade de imagem cinematográfica.", "Sistema Smart fluido e atualizado."])
    return {"pros": pros, "cons": cons}

def generate_long_content(product: Dict[str, Any]) -> str:
    name = product.get("name", "Produto")
    discount = product.get("custom_discount_pct", 0)
    category = product.get("custom_category_slug", "geral").replace("-", " ")
    specs = generate_product_specs(product)
    pros_cons = generate_pros_cons(product)
    
    specs_html = "".join([f"<li><strong>{k}:</strong> {v}</li>" for k, v in specs.items()])
    pros_html = "".join([f"<li>✅ {p}</li>" for p in pros_cons["pros"]])
    cons_html = "".join([f"<li>❌ {c}</li>" for c in pros_cons["cons"]])

    content = f"""
    <p>O <strong>{name}</strong> acaba de entrar no radar de ofertas do Compara Preço com um desconto impressionante de <strong>{discount}%</strong>. Nesta análise técnica, avaliamos se este é o momento ideal para você realizar o investimento ou se deve esperar por uma queda maior.</p>
    
    <h2>1. Por que este produto é destaque hoje?</h2>
    <p>Na categoria de {category}, o {name} sempre foi uma referência de qualidade. Com a redução de preço detectada pelo nosso robô de monitoramento, o produto atingiu um patamar de custo-benefício que raramente vemos fora de épocas como a Black Friday.</p>
    
    <h2>2. Especificações Técnicas</h2>
    <ul>{specs_html}</ul>
    
    <h2>3. Pontos Positivos e Negativos</h2>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
        <div style="background: #e8f5e9; padding: 15px; border-radius: 8px;">
            <h4 style="margin-top:0; color:#2e7d32;">Vantagens</h4>
            <ul style="padding-left: 20px; margin-bottom:0;">{pros_html}</ul>
        </div>
        <div style="background: #ffebee; padding: 15px; border-radius: 8px;">
            <h4 style="margin-top:0; color:#c62828;">Atenção</h4>
            <ul style="padding-left: 20px; margin-bottom:0;">{cons_html}</ul>
        </div>
    </div>
    
    <h2>4. Veredito Final</h2>
    <p>Com base no histórico de preços que monitoramos, o <strong>{name}</strong> está em uma faixa de preço extremamente atrativa. Se você busca um item confiável na categoria de {category}, a compra é altamente recomendada enquanto durarem os estoques promocionais.</p>
    """
    return content

def generate_blog_content(count=1):
    posts_dir = 'noticias/posts'
    os.makedirs(posts_dir, exist_ok=True)
    
    offers_file = 'data/database/all_products.json'
    if not os.path.exists(offers_file):
        logger.error("Banco de dados de produtos não encontrado.")
        return
        
    with open(offers_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    active_products = [p for p in products if p.get('status') == 'active']
    top_products = sorted(active_products, key=lambda x: x.get('custom_discount_pct', 0), reverse=True)[:count]
    
    for product in top_products:
        now = datetime.now()
        p_id = product.get('id')
        p_name = product.get('name', 'Produto')
        
        post_title = f"Análise: Vale a Pena Comprar o {p_name}?"
        post_slug = f"analise-{p_id}-{now.strftime('%Y%m%d')}"
        article_body = generate_long_content(product)
        
        content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post_title} | Compara Preço</title>
    <link rel="stylesheet" href="../../assets/css/style.css">
</head>
<body>
    <header class="header"><div class="container"><a href="../../" class="logo">📊 Compara Preço</a></div></header>
    <main class="container" style="padding: 40px 20px; max-width: 800px; margin: 0 auto;">
        <article>
            <header style="margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px;">
                <div style="color: var(--primary); font-weight: bold; margin-bottom: 10px;">ANÁLISE DE OFERTA</div>
                <h1>{post_title}</h1>
                <p style="color: #666;">Equipe Compara Preço | {now.strftime('%d/%m/%Y')}</p>
            </header>
            
            <div style="background: #f9f9f9; padding: 20px; border-radius: 12px; display: flex; gap: 20px; align-items: center; margin-bottom: 30px;">
                <img src="{product.get('image')}" alt="{p_name}" style="width: 150px; height: 150px; object-fit: contain; background: white; border-radius: 8px;">
                <div>
                    <div style="font-size: 24px; font-weight: 800; color: #d32f2f;">R$ {product.get('price'):.2f}</div>
                    <div style="color: #388e3c; font-weight: bold;">{product.get('custom_discount_pct')}% OFF</div>
                    <a href="{product.get('custom_affiliate_url')}" class="btn" style="margin-top: 15px; display: inline-block;">Ver Oferta no Mercado Livre</a>
                </div>
            </div>

            <div class="content">{article_body}</div>
            
            <div style="margin-top: 40px; text-align: center; border-top: 1px solid #eee; padding-top: 20px;">
                <a href="../../noticias/" style="color: var(--primary); text-decoration: none; font-weight: bold;">← Ver todas as notícias</a>
            </div>
        </article>
    </main>
</body>
</html>
"""
        file_path = os.path.join(posts_dir, f"{post_slug}.html")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        update_news_index(post_title, post_slug, product)

def update_news_index(title, slug, product):
    index_path = 'noticias/index.html'
    if not os.path.exists(index_path): return
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    now = datetime.now()
    new_entry = f"""
    {{
        "id": {int(now.timestamp())},
        "tag": "analise",
        "tagLabel": "📊 Análise",
        "tagClass": "tag-analise",
        "icon": "🔍",
        "title": "{title}",
        "excerpt": "Análise técnica do {product.get('name')[:50]}... com {product.get('custom_discount_pct')}% de desconto.",
        "date": "{now.strftime('%d %b %Y')}",
        "readTime": "5 min",
        "featured": true,
        "url": "posts/{slug}.html"
    }},"""
    
    if "const NEWS = [" in content:
        content = content.replace("const NEWS = [", f"const NEWS = [{new_entry}")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    import sys
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    generate_blog_content(count)
