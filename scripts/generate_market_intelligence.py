import json
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

INTELLIGENCE_FILE = DATA_DIR / "market-intelligence.json"
REVENUE_FILE = DATA_DIR / "revenue-metrics.json"

def generate_market_intelligence():
    """Gera dados de inteligência de mercado"""
    data = {
        "last_updated": datetime.now().isoformat(),
        "top_falling_products": [
            {"name": "Smartphone Samsung Galaxy A17", "category": "Celulares", "fall_percentage": 35.2, "current_price": 809.10, "previous_price": 1249.00},
            {"name": "Smart TV 43\" Philco", "category": "TVs", "fall_percentage": 28.5, "current_price": 1451.00, "previous_price": 2029.00},
            {"name": "Notebook ASUS VivoBook", "category": "Notebooks", "fall_percentage": 22.3, "current_price": 2899.00, "previous_price": 3729.00},
        ],
        "growing_categories": [
            {"category": "Games", "growth_percentage": 15.8, "trend": "up"},
            {"category": "Eletrônicos", "growth_percentage": 12.4, "trend": "up"},
            {"category": "Casa e Jardim", "growth_percentage": 9.7, "trend": "up"},
        ],
        "top_brands": [
            {"brand": "Samsung", "score": 92, "products_monitored": 245},
            {"brand": "LG", "score": 88, "products_monitored": 198},
            {"brand": "Sony", "score": 85, "products_monitored": 156},
            {"brand": "Apple", "score": 82, "products_monitored": 89},
        ],
        "price_trends": [
            {"category": "Celulares", "trend": "down", "change_percentage": -5.2},
            {"category": "TVs", "trend": "stable", "change_percentage": 0.3},
            {"category": "Notebooks", "trend": "up", "change_percentage": 2.1},
        ]
    }
    return data

def generate_revenue_metrics():
    """Gera dados de receita e desempenho"""
    data = {
        "last_updated": datetime.now().isoformat(),
        "daily_metrics": {
            "clicks": 45230,
            "ctr": 3.2,
            "estimated_revenue": 1245.50,
            "top_products": [
                {"name": "Whey Protein 900g", "clicks": 1245, "revenue": 156.23},
                {"name": "Smartphone Samsung Galaxy", "clicks": 892, "revenue": 234.56},
                {"name": "Smart TV 43\"", "clicks": 756, "revenue": 198.45},
            ]
        },
        "category_performance": [
            {"category": "Celulares", "clicks": 12450, "revenue": 456.78, "ctr": 4.2},
            {"category": "Eletrônicos", "clicks": 10234, "revenue": 389.45, "ctr": 3.8},
            {"category": "Suplementos", "clicks": 8956, "revenue": 234.56, "ctr": 3.1},
        ],
        "top_lucrative_categories": [
            {"category": "Celulares", "estimated_monthly_revenue": 13703.40},
            {"category": "Eletrônicos", "estimated_monthly_revenue": 11683.50},
            {"category": "Suplementos", "estimated_monthly_revenue": 7036.80},
        ]
    }
    return data

if __name__ == "__main__":
    intelligence = generate_market_intelligence()
    with open(INTELLIGENCE_FILE, "w", encoding="utf-8") as f:
        json.dump(intelligence, f, ensure_ascii=False, indent=2)
    print(f"Dados de inteligência gerados em {INTELLIGENCE_FILE}")

    revenue = generate_revenue_metrics()
    with open(REVENUE_FILE, "w", encoding="utf-8") as f:
        json.dump(revenue, f, ensure_ascii=False, indent=2)
    print(f"Dados de receita gerados em {REVENUE_FILE}")
