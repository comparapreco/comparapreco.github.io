import json
import os
import unicodedata
from collections import defaultdict
from logger import logger

def slugify(text: str) -> str:
    if not text: return ""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.lower().replace(' ', '-')
    return ''.join(c for c in text if c.isalnum() or c == '-')

def clean_url(url):
    if not url: return ""
    return url.split('?')[0].split('#')[0].rstrip('/')

def deep_clean(db_path):
    if not os.path.exists(db_path):
        logger.error(f"Arquivo {db_path} não encontrado.")
        return

    with open(db_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    total_original = len(products)
    
    # Dicionário para consolidar por slug (nome normalizado)
    consolidated = {}
    
    # Ordenar por desconto (desc) e preço (asc) para manter a melhor oferta
    products.sort(key=lambda x: (x.get('custom_discount_pct', 0), -float(x.get('price', 0))), reverse=True)

    removed_count = 0
    redirects = {}

    for p in products:
        p_id = p.get('id')
        p_name = p.get('name') or p.get('title') or ""
        p_slug = slugify(p_name)
        p_url = clean_url(p.get('permalink') or p.get('url') or p.get('custom_affiliate_url'))
        
        # Chave de consolidação: slug (nome)
        if not p_slug:
            consolidated[p_id] = p
            continue

        is_duplicate = False
        
        # Normalização agressiva: remover "promoção especial", "oferta", etc.
        def super_normalize(s):
            s = s.replace('promocao-especial', '').replace('oferta', '').replace('desconto', '')
            s = s.replace('frete-gratis', '').replace('original', '').replace('lacrado', '')
            return s.strip('-')

        p_norm = super_normalize(p_slug)
        
        for existing_id, existing_p in consolidated.items():
            e_slug = slugify(existing_p.get('name', ''))
            e_norm = super_normalize(e_slug)
            e_url = clean_url(existing_p.get('permalink') or existing_p.get('url') or existing_p.get('custom_affiliate_url'))
            
            # 1. Mesma URL
            if p_url and p_url == e_url:
                is_duplicate = True
                break
            
            # 2. Mesmo Nome Normalizado (Agressivo)
            if p_norm == e_norm and len(p_norm) > 10:
                is_duplicate = True
                break
                
            # 3. Similaridade de Início de Nome
            # Se os primeiros 30 caracteres do slug forem iguais, é o mesmo produto
            if p_slug[:30] == e_slug[:30] and len(p_slug) > 30:
                is_duplicate = True
                break

        if is_duplicate:
            removed_count += 1
            # Mapear para redirecionamento futuro se necessário
            redirects[p_id] = existing_id
        else:
            consolidated[p_id] = p

    final_products = list(consolidated.values())
    
    logger.info(f"Limpeza concluída: {total_original} -> {len(final_products)} ({removed_count} duplicados removidos)")
    
    # Salvar banco limpo
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(final_products, f, ensure_ascii=False, indent=2)
        
    # Salvar mapa de redirecionamentos
    with open("data/duplicates_redirect_map.json", "w", encoding="utf-8") as f:
        json.dump(redirects, f, ensure_ascii=False, indent=2)

    return total_original, len(final_products), removed_count

if __name__ == "__main__":
    deep_clean("data/database/all_products.json")
