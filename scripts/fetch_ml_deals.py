import requests
import json
import os
from logger import logger

def fetch_ml_deals():
    logger.info("Buscando ofertas reais do Mercado Livre...")
    # URL da API de buscas do Mercado Livre (exemplo de ofertas)
    url = "https://api.mercadolibre.com/sites/MLB/search?q=ofertas&limit=50"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            products = []
            for item in results:
                products.append({
                    "id": item.get('id'),
                    "name": item.get('title'),
                    "title": item.get('title'),
                    "price": item.get('price'),
                    "originalPrice": item.get('original_price') or item.get('price'),
                    "permalink": item.get('permalink'),
                    "image": item.get('thumbnail').replace("-I.jpg", "-O.jpg"),
                    "thumbnail": item.get('thumbnail'),
                    "custom_category_slug": "ofertas",
                    "custom_discount_pct": int(((item.get('original_price', item.get('price')) - item.get('price')) / item.get('original_price', 1)) * 100) if item.get('original_price') else 0
                })
            
            os.makedirs("data", exist_ok=True)
            with open("data/curated_products.json", "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            logger.info(f"Sucesso: {len(products)} ofertas reais salvas.")
            return True
        else:
            logger.error(f"Erro na API do ML: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Erro ao buscar ofertas: {e}")
        return False

if __name__ == "__main__":
    fetch_ml_deals()
