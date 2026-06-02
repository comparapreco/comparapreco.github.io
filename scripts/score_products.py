"""
score_products.py — Camada de Qualidade e Inteligência Comercial
Implementa:
  - quality_score (0-100): filtra produtos com score < 70
  - price_anomaly: detecta descontos artificiais
  - trend_score (0-100): identifica produtos em tendência
  - brand_priority: prioriza marcas premium
"""
import os
import json
from datetime import datetime
from logger import logger

QUALITY_THRESHOLD = 70
MAX_FAKE_DISCOUNT_RATIO = 3.5

PREMIUM_BRANDS = [
    "samsung", "lg", "apple", "xiaomi", "dell", "lenovo", "asus",
    "motorola", "sony", "philips", "braun", "bosch", "whirlpool",
    "electrolux", "panasonic", "jbl", "multilaser", "intelbras"
]

STOCK_BLOCK_TERMS = [
    "última unidade", "ultima unidade", "sem estoque",
    "indisponível", "indisponivel", "esgotado", "fora de estoque"
]

BLACKLIST_TERMS = [
    "capinha", "película", "pelicula", "adaptador genérico",
    "adaptador generico", "cabo sem marca", "case genérico",
    "case generico", "película protetora", "suporte genérico"
]

def _brand_in_name(name):
    name_lower = name.lower()
    for brand in PREMIUM_BRANDS:
        if brand in name_lower:
            return brand
    return None

def _has_real_image(product):
    img = product.get("image") or product.get("thumbnail") or ""
    return img.startswith("http") and len(img) > 20

def _title_quality(name):
    if not name:
        return 0
    score = 0
    if len(name) >= 20:
        score += 10
    if len(name) >= 40:
        score += 5
    if _brand_in_name(name):
        score += 5
    return min(score, 20)

def _discount_score(discount_pct):
    if discount_pct <= 0:
        return 0
    if discount_pct >= 50:
        return 30
    if discount_pct >= 30:
        return 20
    if discount_pct >= 15:
        return 10
    return 5

def _detect_price_anomaly(product):
    price = float(product.get("price") or 0)
    original = float(product.get("original_price") or product.get("originalPrice") or 0)
    if price <= 0 or original <= 0:
        return False
    ratio = original / price
    discount = ((original - price) / original) * 100
    if discount > 70 and ratio > MAX_FAKE_DISCOUNT_RATIO:
        return True
    if discount > 60 and (original % 100 == 0 or original % 50 == 0):
        return True
    return False

def _compute_quality_score(product):
    score = 0
    discount = float(product.get("custom_discount_pct") or 0)
    score += _discount_score(discount)
    if _has_real_image(product):
        score += 15
    score += _title_quality(product.get("name") or product.get("title") or "")
    if _brand_in_name(product.get("name") or product.get("title") or ""):
        score += 20
    if not _detect_price_anomaly(product):
        score += 15
    return min(score, 100)

def _compute_trend_score(product, appearance_count):
    score = 0
    pid = product.get("id") or ""
    count = appearance_count.get(pid, 1)
    score += min(count, 5) * 8
    discount = float(product.get("custom_discount_pct") or 0)
    if discount >= 40:
        score += 30
    elif discount >= 20:
        score += 20
    elif discount >= 10:
        score += 10
    if _brand_in_name(product.get("name") or ""):
        score += 20
    if product.get("is_price_drop"):
        score += 10
    return min(score, 100)

def _is_blacklisted_term(name):
    name_lower = name.lower()
    return any(term in name_lower for term in BLACKLIST_TERMS)

def _has_stock_issue(product):
    name_lower = (product.get("name") or "").lower()
    return any(term in name_lower for term in STOCK_BLOCK_TERMS)

def _save_cycle_metrics(stats):
    metrics_path = "data/cycle_metrics.json"
    history = []
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
    entry = {
        "timestamp": datetime.now().isoformat(),
        "produtos_processados": stats.get("total_raw", 0),
        "publicados": stats.get("approved", 0),
        "bloqueados": (
            stats.get("blocked_blacklist", 0) +
            stats.get("blocked_stock", 0) +
            stats.get("blocked_price_anomaly", 0) +
            stats.get("blocked_low_quality", 0)
        ),
        "duplicados": stats.get("blocked_duplicate", 0),
        "recategorizados": 0,
        "detalhes": stats
    }
    history.append(entry)
    history = history[-100:]
    os.makedirs("data", exist_ok=True)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def process(input_p, output_p):
    if not os.path.exists(input_p):
        logger.warning(f"Arquivo de entrada não encontrado: {input_p}")
        products = []
        stats = {"total_raw": 0, "approved": 0, "blocked_duplicate": 0,
                 "blocked_blacklist": 0, "blocked_stock": 0,
                 "blocked_price_anomaly": 0, "blocked_low_quality": 0}
    else:
        with open(input_p, "r", encoding="utf-8") as f:
            try:
                raw_data = json.load(f)
            except Exception as e:
                logger.error(f"Erro ao ler {input_p}: {e}")
                raw_data = []

        appearance_count = {}
        for p in raw_data:
            pid = p.get("id") or ""
            appearance_count[pid] = appearance_count.get(pid, 0) + 1

        products = []
        seen_ids = set()
        stats = {
            "total_raw": len(raw_data),
            "blocked_duplicate": 0,
            "blocked_blacklist": 0,
            "blocked_stock": 0,
            "blocked_price_anomaly": 0,
            "blocked_low_quality": 0,
            "approved": 0
        }

        for p in raw_data:
            p_id = p.get("id")
            name = p.get("name") or p.get("title") or ""
            price = p.get("price", 0)

            if not p_id or not name or price <= 0:
                continue

            if p_id in seen_ids:
                stats["blocked_duplicate"] += 1
                continue
            seen_ids.add(p_id)

            if _is_blacklisted_term(name):
                stats["blocked_blacklist"] += 1
                continue

            if _has_stock_issue(p):
                stats["blocked_stock"] += 1
                continue

            price_anomaly = _detect_price_anomaly(p)
            p["price_anomaly"] = price_anomaly
            if price_anomaly:
                stats["blocked_price_anomaly"] += 1
                continue

            quality_score = _compute_quality_score(p)
            p["quality_score"] = quality_score
            if quality_score < QUALITY_THRESHOLD:
                stats["blocked_low_quality"] += 1
                continue

            p["trend_score"] = _compute_trend_score(p, appearance_count)
            brand = _brand_in_name(name)
            p["brand_priority"] = brand is not None
            p["brand_name"] = brand or ""

            stats["approved"] += 1
            products.append(p)

    os.makedirs(os.path.dirname(output_p), exist_ok=True)
    with open(output_p, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    logger.info(
        f"Scoring: {stats.get('approved', len(products))} aprovados | "
        f"blacklist={stats.get('blocked_blacklist',0)} "
        f"estoque={stats.get('blocked_stock',0)} "
        f"anomalia={stats.get('blocked_price_anomaly',0)} "
        f"qualidade={stats.get('blocked_low_quality',0)} "
        f"duplicados={stats.get('blocked_duplicate',0)}"
    )
    _save_cycle_metrics(stats)

if __name__ == "__main__":
    process("data/raw_products.json", "data/scored_products.json")
