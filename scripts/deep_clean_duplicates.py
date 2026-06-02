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
        # Se o slug for muito curto, ignorar
        if len(p_slug) < 5:
            consolidated[p_id] = p
            continue

        is_duplicate = False
        
        # Verificar se já existe um produto com slug idêntico ou URL idêntica
        for existing_id, existing_p in consolidated.items():
            e_slug = slugify(existing_p.get('name', ''))
            e_url = clean_url(existing_p.get('permalink') or existing_p.get('url') or existing_p.get('custom_affiliate_url'))
            
            # 1. Mesma URL
            if p_url and p_url == e_url:
                is_duplicate = True
                break
            
            # 2. Mesmo Nome (Slug)
            if p_slug == e_slug:
                is_duplicate = True
                break
                
            # 3. Detecção de "Promoção Especial" ou nomes genéricos repetidos
            if "promocao-especial" in p_slug and "promocao-especial" in e_slug:
                # Se os primeiros 20 caracteres do nome original forem iguais
                if p_name[:20] == existing_p.get('name', '')[:20]:
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
