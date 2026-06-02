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

def super_normalize(s):
    if not s: return ""
    # Remover ruídos comuns que geram duplicatas
    s = s.replace('promocao-especial', '').replace('oferta', '').replace('desconto', '')
    s = s.replace('frete-gratis', '').replace('original', '').replace('lacrado', '')
    s = s.replace('unidade', '').replace('kit', '').replace('com-ia', '')
    # Remover palavras muito curtas (ruído)
    s = '-'.join([w for w in s.split('-') if len(w) > 2])
    return s.strip('-')

def clean_url(url):
    if not url: return ""
    return url.split('?')[0].split('#')[0].rstrip('/')

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
    products.sort(key=lambda x: (x.get('custom_discount_pct', 0), -float(x.get('price', 0)), x.get('id', '')), reverse=True)

    for p in products:
        p_id = p.get('id')
        if not p_id: continue
            
        p_url = clean_url(p.get('permalink') or p.get('url') or p.get('custom_affiliate_url'))
        p_name = p.get('name') or p.get('title') or ""
        p_slug = slugify(p_name)
        p_norm = super_normalize(p_slug)
        
        # Chaves de deduplicação agressiva
        # 1. Por ID exato
        if p_id in unique_products:
            continue
            
        is_duplicate = False
        for up in unique_products.values():
            up_url = clean_url(up.get('permalink') or up.get('url') or up.get('custom_affiliate_url'))
            up_name = up.get('name') or up.get('title') or ""
            up_slug = slugify(up_name)
            up_norm = super_normalize(up_slug)
            
            # 2. Mesma URL limpa
            if p_url and p_url == up_url:
                is_duplicate = True
                break
                
            # 3. Mesmo Nome Normalizado (Agressivo)
            if p_norm == up_norm and len(p_norm) > 10:
                is_duplicate = True
                break
            
            # 4. Similaridade de Início de Nome (20 chars)
            if p_slug[:20] == up_slug[:20] and len(p_slug) > 20:
                is_duplicate = True
                break
                
            # 5. Detecção de IDs no final da URL
            if p_id in str(up_url):
                is_duplicate = True
                break

        if not is_duplicate:
            unique_products[p_id] = p

    final_products = list(unique_products.values())
    total_removed = total_original - len(final_products)
    logger.info(f"Deduplicação concluída: {total_original} -> {len(final_products)} ({total_removed} removidos).")
    
    os.makedirs(os.path.dirname(output_p), exist_ok=True)
    with open(output_p, "w", encoding="utf-8") as f:
        json.dump(final_products, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process("data/validated_products.json", "data/new_offers.json")
