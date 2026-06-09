import json
import requests
import os
import time
from logger import logger

def audit_products(input_path: str, output_path: str, affiliate_tag: str):
    logger.info(f"Iniciando auditoria rigorosa em {input_path}...")
    
    if not os.path.exists(input_path):
        logger.error("Arquivo de entrada não encontrado.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        products = json.load(f)

    valid_products = []
    errors = {
        "image_failed": 0,
        "price_invalid": 0,
        "affiliate_missing": 0,
        "placeholder_image": 0
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for i, p in enumerate(products):
        p_id = p.get('id', 'N/A')
        p_name = p.get('name', 'N/A')
        img_url = p.get('image') or p.get('thumbnail') or ''
        aff_url = p.get('custom_affiliate_url', '')
        price = p.get('price', 0)

        # 1. Verificar Imagem
        is_valid_img = False
        if img_url and "placehold.jp" not in img_url:
            try:
                # Verificar se a imagem realmente existe (HEAD request)
                resp = requests.head(img_url, headers=headers, timeout=5, allow_redirects=True)
                if resp.status_code == 200:
                    is_valid_img = True
                else:
                    errors["image_failed"] += 1
            except:
                errors["image_failed"] += 1
        else:
            errors["placeholder_image"] += 1

        # 2. Verificar Preço
        is_valid_price = isinstance(price, (int, float)) and price > 0
        if not is_valid_price:
            errors["price_invalid"] += 1

        # 3. Verificar Link de Afiliado
        is_valid_aff = affiliate_tag in aff_url
        if not is_valid_aff:
            # Tentar corrigir o link se estiver faltando a tag
            if aff_url:
                separator = '&' if '?' in aff_url else '?'
                aff_url = f"{aff_url}{separator}matt_tool={affiliate_tag}"
                p['custom_affiliate_url'] = aff_url
                is_valid_aff = True
            else:
                errors["affiliate_missing"] += 1

        # Decisão Final: Só entra se estiver PERFEITO
        if is_valid_img and is_valid_price and is_valid_aff:
            valid_products.append(p)
            if len(valid_products) % 10 == 0:
                logger.info(f"Auditados: {i+1}/{len(products)} | Válidos: {len(valid_products)}")
        
        # Pausa para não ser bloqueado pelo ML
        if i % 20 == 0:
            time.sleep(1)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(valid_products, f, indent=2, ensure_ascii=False)

    logger.info(f"Auditoria concluída!")
    logger.info(f"Total Inicial: {len(products)}")
    logger.info(f"Total Válido: {len(valid_products)}")
    logger.info(f"Erros encontrados: {errors}")

if __name__ == "__main__":
    audit_products(
        "data/database/all_products.json", 
        "data/database/audited_products.json", 
        "60566305"
    )
