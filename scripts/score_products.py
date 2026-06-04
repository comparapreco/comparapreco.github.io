import json
import os
from logger import logger

RAW_FILE = "data/raw_products.json"
SCORED_FILE = "data/scored_products.json"
METRICS_FILE = "data/cycle_metrics.json"

# Configurações de Filtro
MIN_QUALITY_SCORE = 55 # Reduzido de 70 para 55 para permitir mais ofertas reais
MAX_DISCOUNT_PCT = 85  # Aumentado de 70 para 85 (existem queimas de estoque reais de 80%)

def calculate_score(product):
    score = 50 # Base
    
    # 1. Foto Obrigatória (CRÍTICO)
    # Bloqueia se não tiver imagem ou se for placeholder comum
    image = product.get('image') or product.get('thumbnail') or ''
    if not image or 'placeholder' in image.lower() or 'no-image' in image.lower():
        return 0, "Sem imagem válida"

    # 2. Desconto Real
    discount = product.get('custom_discount_pct', 0)
    if discount > MAX_DISCOUNT_PCT:
        return 0, "Anomalia de preço (desconto excessivo)"
    
    score += (discount * 0.6) # Aumentado peso do desconto

    # 3. Marcas Premium
    premium_brands = ['apple', 'samsung', 'motorola', 'xiaomi', 'dell', 'asus', 'lg', 'philips', 'sony']
    name_lower = product.get('name', '').lower()
    if any(brand in name_lower for brand in premium_brands):
        score += 20 # Bônus para marcas conhecidas

    # 4. Blacklist de Termos
    blacklist = ['capinha', 'pelicula', 'usado', 'recondicionado', 'vitrine', 'quebrado', 'defeito']
    if any(term in name_lower for term in blacklist):
        return 0, "Produto em blacklist"

    # 5. Termos de Estoque
    stock_terms = ['esgotado', 'sem estoque', 'ultima unidade']
    if any(term in name_lower for term in stock_terms):
        return 0, "Sem estoque"

    return min(100, score), "Aprovado"

def process_scoring():
    if not os.path.exists(RAW_FILE):
        return
    
    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    scored_list = []
    metrics = {
        "total_raw": len(products),
        "blocked_no_image": 0,
        "blocked_blacklist": 0,
        "blocked_stock": 0,
        "blocked_price_anomaly": 0,
        "blocked_low_quality": 0,
        "approved": 0
    }

    for p in products:
        score, reason = calculate_score(p)
        p['quality_score'] = score
        
        if score == 0:
            if "imagem" in reason: metrics["blocked_no_image"] += 1
            elif "blacklist" in reason: metrics["blocked_blacklist"] += 1
            elif "estoque" in reason: metrics["blocked_stock"] += 1
            elif "anomalia" in reason: metrics["blocked_price_anomaly"] += 1
            continue
            
        if score < MIN_QUALITY_SCORE:
            metrics["blocked_low_quality"] += 1
            continue
            
        metrics["approved"] += 1
        scored_list.append(p)

    with open(SCORED_FILE, 'w', encoding='utf-8') as f:
        json.dump(scored_list, f, ensure_ascii=False, indent=2)

    # Salvar métricas do ciclo
    cycle_data = {
        "timestamp": os.popen('date -Iseconds').read().strip(),
        "produtos_processados": metrics["total_raw"],
        "publicados": metrics["approved"],
        "detalhes": metrics
    }
    
    history = []
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, 'r') as f: history = json.load(f)
    history.append(cycle_data)
    with open(METRICS_FILE, 'w') as f: json.dump(history[-50:], f, indent=2)

    logger.info(f"Scoring: {metrics['approved']} aprovados | sem_foto={metrics['blocked_no_image']} anomalia={metrics['blocked_price_anomaly']}")

if __name__ == "__main__":
    process_scoring()
