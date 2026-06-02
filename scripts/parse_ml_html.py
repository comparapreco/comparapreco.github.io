from bs4 import BeautifulSoup
import json
import os
import re

def parse_ml_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    products = []
    # O Mercado Livre usa 'poly-card' para os itens de oferta agora
    cards = soup.select('.poly-card')
    
    for card in cards:
        try:
            title_tag = card.select_one('.poly-component__title a')
            if not title_tag: continue
            
            name = title_tag.text.strip()
            link = title_tag.get('href', '')
            
            # Preço atual
            price_fraction = card.select_one('.andes-money-amount__fraction')
            price_cents = card.select_one('.andes-money-amount__cents')
            price_str = price_fraction.text.replace('.', '') if price_fraction else "0"
            if price_cents:
                price_str += "." + price_cents.text
            price = float(price_str)
            
            # Preço original (se houver)
            old_price_tag = card.select_one('.andes-money-amount--previous .andes-money-amount__fraction')
            if old_price_tag:
                old_price = float(old_price_tag.text.replace('.', ''))
            else:
                old_price = price # Fallback
                
            # ID do produto
            mlb_id_match = re.search(r'MLB-?(\d+)', link)
            if not mlb_id_match:
                mlb_id_match = re.search(r'wid=MLB(\d+)', link)
            
            mlb_id = f"MLB{mlb_id_match.group(1)}" if mlb_id_match else f"GEN{hash(link) % 10000000}"
            
            # Imagem
            img_tag = card.select_one('.poly-card__portada img')
            image = img_tag.get('data-src') or img_tag.get('src') if img_tag else ""
            
            products.append({
                "id": mlb_id,
                "name": name,
                "price": price,
                "original_price": old_price,
                "permalink": link,
                "image": image,
                "status": "active"
            })
        except Exception as e:
            continue
            
    return products

if __name__ == "__main__":
    html_file = "/home/ubuntu/browser_html/mercadolivre_com_br_ofertas_1780419313666.html"
    if os.path.exists(html_file):
        prods = parse_ml_html(html_file)
        print(json.dumps(prods, indent=2, ensure_ascii=False))
    else:
        print("[]")
