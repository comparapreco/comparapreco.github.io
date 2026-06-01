import json
import os
from datetime import datetime
from pathlib import Path
from logger import logger

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATABASE_FILE = DATA_DIR / "database" / "all_products.json"
EDITORIAL_FILE = DATA_DIR / "editorial-automation.json"

def generate_editorial_content():
    """Gera conteúdo editorial real baseado nos produtos com maiores descontos."""
    if not DATABASE_FILE.exists():
        logger.error(f"Banco de dados não encontrado em {DATABASE_FILE}")
        return None

    try:
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            products = json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler banco de dados: {e}")
        return None

    # Filtrar apenas produtos ativos e com desconto relevante (> 30%)
    active_offers = [p for p in products if p.get('status') == 'active' and p.get('custom_discount_pct', 0) >= 30]
    
    # Ordenar pelos maiores descontos
    top_offers = sorted(active_offers, key=lambda x: x.get('custom_discount_pct', 0), reverse=True)[:5]

    articles = []
    triggers = []

    for p in top_offers:
        p_id = p.get('id')
        name = p.get('name')
        discount = p.get('custom_discount_pct')
        price = p.get('price')
        old_price = p.get('original_price') or p.get('originalPrice')
        category = p.get('custom_category_slug', 'Geral').title()
        
        slug = f"{name.lower().replace(' ', '-')[:50]}-queda-{discount}"
        
        article = {
            "id": f"article-{p_id}",
            "title": f"{name}: Queda Histórica de {discount}% OFF!",
            "slug": slug,
            "category": category,
            "price_drop": discount,
            "current_price": price,
            "previous_price": old_price,
            "status": "published",
            "generated_at": datetime.now().isoformat(),
            "content": f"O {name} atingiu uma queda de {discount}% em seu preço. Agora disponível por apenas R$ {price:.2f}, este é um dos melhores momentos para adquirir este produto monitorado pelo Compara Preço.",
            "social_posts": [
                {
                    "platform": "twitter",
                    "content": f"📱 ALERTA: {name} com {discount}% de desconto! De R$ {old_price:.2f} por apenas R$ {price:.2f}. Aproveite! 🔥 #ComparaPreço #Oferta"
                }
            ]
        }
        articles.append(article)
        
        triggers.append({
            "product_id": p_id,
            "product_name": name,
            "price_drop_threshold": 30,
            "current_drop": discount,
            "alert_sent": True,
            "alert_timestamp": datetime.now().isoformat()
        })

    return {
        "last_generated": datetime.now().isoformat(),
        "automated_articles": articles,
        "alert_triggers": triggers
    }

if __name__ == "__main__":
    data = generate_editorial_content()
    if data:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(EDITORIAL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Sucesso: {len(data['automated_articles'])} artigos reais gerados em {EDITORIAL_FILE}")
