import json
import os
import random
from datetime import datetime
from pathlib import Path
from logger import logger

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATABASE_FILE = DATA_DIR / "database" / "all_products.json"
EDITORIAL_FILE = DATA_DIR / "editorial-automation.json"

# Termos proibidos para evitar repetição excessiva (como solicitado pelo usuário)
FORBIDDEN_TERMS = ["whey", "creatina", "dark lab", "suplemento"]

def generate_editorial_content():
    """Gera conteúdo editorial real com DIVERSIFICAÇÃO de categorias."""
    if not DATABASE_FILE.exists():
        logger.error(f"Banco de dados não encontrado em {DATABASE_FILE}")
        return None

    try:
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            products = json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler banco de dados: {e}")
        return None

    # 1. Filtrar apenas produtos ativos e com desconto relevante (> 30%)
    # 2. Excluir termos proibidos (Whey/Vírus)
    active_offers = []
    for p in products:
        name_lower = p.get('name', '').lower()
        is_forbidden = any(term in name_lower for term in FORBIDDEN_TERMS)
        
        if p.get('status') == 'active' and p.get('custom_discount_pct', 0) >= 30 and not is_forbidden:
            active_offers.append(p)
    
    if not active_offers:
        logger.warning("Nenhuma oferta encontrada após filtrar termos proibidos. Relaxando filtros...")
        active_offers = [p for p in products if p.get('status') == 'active' and p.get('custom_discount_pct', 0) >= 20]

    # 3. Agrupar por categoria para garantir diversidade
    by_category = {}
    for p in active_offers:
        cat = p.get('custom_category_slug', 'geral')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(p)

    # 4. Escolher o melhor de cada categoria (máximo 5 categorias diferentes)
    diverse_offers = []
    categories = list(by_category.keys())
    random.shuffle(categories) # Aleatoriedade para não vir sempre a mesma ordem
    
    for cat in categories[:5]:
        # Pegar o melhor desconto desta categoria
        best_in_cat = sorted(by_category[cat], key=lambda x: x.get('custom_discount_pct', 0), reverse=True)[0]
        diverse_offers.append(best_in_cat)

    # 5. Ordenar a seleção final pelo maior desconto entre as escolhidas
    top_offers = sorted(diverse_offers, key=lambda x: x.get('custom_discount_pct', 0), reverse=True)

    articles = []
    triggers = []

    for p in top_offers:
        p_id = p.get('id')
        name = p.get('name')
        discount = p.get('custom_discount_pct')
        price = p.get('price')
        old_price = p.get('original_price') or p.get('originalPrice')
        category = p.get('custom_category_slug', 'Geral').title()
        
        # Criar slug limpo
        clean_name = "".join([c if c.isalnum() else "-" for c in name.lower()]).replace("--", "-")
        slug = f"{clean_name[:50]}-queda-{discount}"
        
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
        logger.info(f"Sucesso: {len(data['automated_articles'])} artigos diversificados gerados em {EDITORIAL_FILE}")
