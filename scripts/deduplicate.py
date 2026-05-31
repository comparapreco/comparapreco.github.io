import os
import json
import unicodedata
from logger import logger

def slugify(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.lower().replace(' ', '-')
    return ''.join(c for c in text if c.isalnum() or c == '-')

def process(input_p: str, output_p: str):
    if not os.path.exists(input_p):
        logger.warning(f"Arquivo de entrada {input_p} não encontrado.")
        products = []
    else:
        with open(input_p, "r", encoding="utf-8") as f:
            products = json.load(f)

    total_original = len(products)
    unique_products = {}
    
    # Ordenar por maior desconto e menor preço para garantir que a melhor oferta sobreviva
    # Também usamos o ID como critério de desempate para consistência
    products.sort(key=lambda x: (x.get('custom_discount_pct', 0), -float(x.get('price', 0)), x.get('id', '')), reverse=True)

    for p in products:
        p_id = p.get('id')
        if not p_id:
            continue
            
        p_url = p.get('permalink') or p.get('url') or p.get('custom_affiliate_url')
        p_name = p.get('name') or p.get('title') or ""
        p_price = float(p.get('price', 0))
        p_slug = slugify(p_name)
        
        # Chaves de deduplicação agressiva
        # 1. Por ID exato
        if p_id in unique_products:
            continue
            
        # 2. Por URL (ignorando parâmetros de tracking)
        def clean_url(url):
            if not url: return ""
            return url.split('?')[0].split('#')[0].rstrip('/')

        p_url_clean = clean_url(p_url)
        
        is_duplicate = False
        for up in unique_products.values():
            up_url = up.get('permalink') or up.get('url') or up.get('custom_affiliate_url')
            up_name = up.get('name') or up.get('title') or ""
            up_price = float(up.get('price', 0))
            up_slug = slugify(up_name)
            
            # Verificação de URL limpa
            if p_url_clean and clean_url(up_url) == p_url_clean:
                is_duplicate = True
                break
                
            # Verificação de Nome (Slug) e Preço similar (variação < 1%)
            if p_slug == up_slug:
                price_diff = abs(p_price - up_price)
                if up_price > 0 and (price_diff / up_price) < 0.01:
                    is_duplicate = True
                    break
            
            # Verificação de ID no final da URL (comum no ML)
            if p_id in str(up_url):
                is_duplicate = True
                break

        if not is_duplicate:
            unique_products[p_id] = p

    final_products = list(unique_products.values())
    total_removed = total_original - len(final_products)
    logger.info(f"Deduplicação concluída: {total_original} produtos processados, {total_removed} duplicados removidos.")
    
    os.makedirs(os.path.dirname(output_p), exist_ok=True)
    with open(output_p, "w", encoding="utf-8") as f:
        json.dump(final_products, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process("data/validated_products.json", "data/new_offers.json")
