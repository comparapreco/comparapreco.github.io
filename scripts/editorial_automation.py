import os
import json
import random
from datetime import datetime
from logger import logger

DATABASE_FILE = "data/database/all_products.json"
EDITORIAL_FILE = "data/editorial-automation.json"

def generate_editorial_content():
    if not os.path.exists(DATABASE_FILE):
        return None
        
    with open(DATABASE_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)
        
    # Prioriza quedas de preço, depois produtos novos (ordenados por desconto)
    price_drops = [p for p in products if p.get("is_price_drop")]
    others = [p for p in products if not p.get("is_price_drop") and p.get("custom_discount_pct", 0) >= 15]
    
    candidates = price_drops + sorted(others, key=lambda x: x.get("custom_discount_pct", 0), reverse=True)
    
    if not candidates:
        return None
        
    # Seleciona os 3 melhores para gerar notícias nesta rodada
    selected = candidates[:3]
    articles = []
    
    for p in selected:
        name = p.get('name')
        discount = p.get('custom_discount_pct')
        price = p.get('price')
        old_price = p.get('original_price') or p.get('originalPrice')
        category = p.get('custom_category_slug', 'Ofertas').title()
        
        is_drop = p.get("is_price_drop")
        title = f"{name}: Queda Histórica de {discount}% OFF!" if is_drop else f"OFERTA: {name} com {discount}% de Desconto"
        
        clean_name = "".join([c if c.isalnum() else "-" for c in name.lower()]).replace("--", "-")
        slug = f"{clean_name[:50]}-queda-{discount}"
        
        content = f"O {name} atingiu uma queda de {discount}% em seu preço. "
        if is_drop:
            content += f"Detectamos uma redução significativa em relação ao preço anterior de R$ {p.get('old_price_recorded', old_price):.2f}. "
        content += f"Agora disponível por apenas R$ {price:.2f}, este é um dos melhores momentos para adquirir este produto monitorado pelo Radar Ninja."
        
        article = {
            "id": f"article-{p['id']}",
            "title": title,
            "slug": slug,
            "category": category,
            "price_drop": discount,
            "current_price": price,
            "previous_price": old_price,
            "status": "published",
            "generated_at": datetime.now().isoformat(),
            "content": content,
            "social_posts": [{"platform": "twitter", "content": f"🔥 {title} por apenas R$ {price:.2f}! Confira no Radar Ninja."}]
        }
        articles.append(article)
        
    return {
        "last_generated": datetime.now().isoformat(),
        "automated_articles": articles,
        "alert_triggers": [{"product_id": p['id'], "product_name": p['name']} for p in selected]
    }

if __name__ == "__main__":
    data = generate_editorial_content()
    if data:
        with open(EDITORIAL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Sucesso: {len(data['automated_articles'])} artigos gerados.")
