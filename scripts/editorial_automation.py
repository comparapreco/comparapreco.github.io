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
HISTORY_FILE = DATA_DIR / "automation-history.json"

# Termos proibidos (como solicitado pelo usuário)
FORBIDDEN_TERMS = ["whey", "creatina", "dark lab", "suplemento"]

def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"published_ids": [], "last_categories": []}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def generate_editorial_content():
    """Gera conteúdo com RODÍZIO de categorias e NÃO REPETIÇÃO de produtos."""
    if not DATABASE_FILE.exists():
        logger.error(f"Banco de dados não encontrado em {DATABASE_FILE}")
        return None

    try:
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            products = json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler banco de dados: {e}")
        return None

    history = load_history()
    published_ids = set(history.get("published_ids", []))
    last_categories = history.get("last_categories", [])

    # 1. Filtrar produtos válidos
    valid_products = []
    for p in products:
        p_id = p.get('id')
        name_lower = p.get('name', '').lower()
        is_forbidden = any(term in name_lower for term in FORBIDDEN_TERMS)
        
        if (p.get('status') == 'active' and 
            p.get('custom_discount_pct', 0) >= 20 and 
            not is_forbidden and 
            p_id not in published_ids):
            valid_products.append(p)
    
    if not valid_products:
        logger.warning("Sem produtos novos! Resetando histórico de IDs para permitir re-postagem...")
        published_ids = set()
        # Tentar filtrar novamente
        valid_products = [p for p in products if p.get('status') == 'active' and not any(t in p.get('name','').lower() for t in FORBIDDEN_TERMS)]

    # 2. Agrupar por categoria
    by_category = {}
    for p in valid_products:
        cat = p.get('custom_category_slug', 'geral')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(p)

    # 3. Escolher a categoria da vez (Rodízio)
    available_categories = [c for c in by_category.keys() if c not in last_categories[-3:]]
    if not available_categories:
        available_categories = list(by_category.keys())
    
    chosen_category = random.choice(available_categories)
    
    # 4. Pegar o melhor produto dessa categoria
    best_product = sorted(by_category[chosen_category], key=lambda x: x.get('custom_discount_pct', 0), reverse=True)[0]
    
    # 5. Atualizar histórico
    history["published_ids"].append(best_product['id'])
    history["last_categories"].append(chosen_category)
    # Manter histórico limpo
    if len(history["published_ids"]) > 500: history["published_ids"] = history["published_ids"][-500:]
    if len(history["last_categories"]) > 10: history["last_categories"] = history["last_categories"][-10:]
    save_history(history)

    # 6. Gerar o artigo único (um por vez como solicitado)
    p = best_product
    p_id = p.get('id')
    name = p.get('name')
    discount = p.get('custom_discount_pct')
    price = p.get('price')
    old_price = p.get('original_price') or p.get('originalPrice')
    category = chosen_category.title()
    
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

    return {
        "last_generated": datetime.now().isoformat(),
        "automated_articles": [article],
        "alert_triggers": [{
            "product_id": p_id,
            "product_name": name,
            "current_drop": discount,
            "alert_timestamp": datetime.now().isoformat()
        }]
    }

if __name__ == "__main__":
    data = generate_editorial_content()
    if data:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(EDITORIAL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Sucesso: 1 artigo de rodízio gerado ({data['automated_articles'][0]['category']}) em {EDITORIAL_FILE}")
