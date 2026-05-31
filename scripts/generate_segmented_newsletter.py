import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

NEWSLETTER_FILE = DATA_DIR / "segmented-newsletter.json"

def generate_segmented_newsletter():
    """Gera dados de newsletter segmentada por categorias"""
    data = {
        "last_generated": "2026-05-31T12:00:00Z",
        "segments": [
            {
                "name": "Celulares",
                "emoji": "📱",
                "description": "Últimas novidades em smartphones, tablets e acessórios",
                "top_offers": [
                    {"name": "Samsung Galaxy A17", "price": 809.10, "discount": "35%"},
                    {"name": "Motorola Moto G35", "price": 869.00, "discount": "28%"},
                ]
            },
            {
                "name": "TVs",
                "emoji": "📺",
                "description": "Smart TVs, OLED, 4K e as melhores promoções",
                "top_offers": [
                    {"name": "Smart TV 43\" Philco", "price": 1451.00, "discount": "28%"},
                    {"name": "Smart TV 50\" Philco", "price": 1994.00, "discount": "22%"},
                ]
            },
            {
                "name": "Notebooks",
                "emoji": "💻",
                "description": "Laptops para trabalho, estudo e gaming",
                "top_offers": [
                    {"name": "Notebook ASUS VivoBook", "price": 2899.00, "discount": "22%"},
                ]
            },
            {
                "name": "Games",
                "emoji": "🎮",
                "description": "Consoles, jogos e periféricos para gamers",
                "top_offers": [
                    {"name": "PlayStation 5", "price": 4999.00, "discount": "15%"},
                ]
            },
            {
                "name": "Casa",
                "emoji": "🏠",
                "description": "Móveis, decoração e utensílios para sua casa",
                "top_offers": [
                    {"name": "Sofá 3 Lugares", "price": 1299.00, "discount": "20%"},
                ]
            }
        ]
    }
    return data

if __name__ == "__main__":
    data = generate_segmented_newsletter()
    with open(NEWSLETTER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Newsletter segmentada gerada em {NEWSLETTER_FILE}")
