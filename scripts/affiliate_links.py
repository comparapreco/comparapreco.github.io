import os
import json
import re
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

# Configurações de Afiliado
ML_AFILIADO_ID = os.environ.get("ML_AFILIADO_ID", "vendas0nline")
AMZ_AFILIADO_ID = os.environ.get("AMZ_AFILIADO_ID", "radar041-20")

def build_affiliate_url(product: dict) -> str:
    """
    Garante que a URL do produto tenha a tag de afiliado correta.
    """
    name = product.get("name", "Produto")
    permalink = product.get("permalink", "")
    current_affiliate = product.get("custom_affiliate_url", "")
    
    # Prioriza o link que já existe, senão usa o permalink
    base_url = current_affiliate if current_affiliate else permalink
    
    if not base_url:
        product_id = product.get("id", "")
        if product_id.startswith("MLB"):
            base_url = f"https://www.mercadolivre.com.br/p/{product_id}"
        else:
            return ""

    parsed = urlparse(base_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    
    # Lógica para Mercado Livre
    if "mercadolivre.com.br" in parsed.netloc:
        params["matt_tool"] = [ML_AFILIADO_ID]
        params["utm_source"] = ["social"]
        params["utm_medium"] = ["ninja"]
        # Remove parâmetros que podem interferir se necessário
    
    # Lógica para Amazon
    elif "amazon.com.br" in parsed.netloc:
        params["tag"] = [AMZ_AFILIADO_ID]
        
    # Reconstrói a URL
    new_query = urlencode({k: v[0] for k, v in params.items()})
    new_url = urlunparse(parsed._replace(query=new_query))
    
    return new_url

def process(input_p: str, output_p: str):
    if not os.path.exists(input_p):
        logger.warning(f"Arquivo não encontrado: {input_p}")
        return
        
    with open(input_p, "r", encoding="utf-8") as f:
        products = json.load(f)
        
    corrected = 0
    for product in products:
        old_url = product.get("custom_affiliate_url", "")
        new_url = build_affiliate_url(product)
        
        if new_url and old_url != new_url:
            product["custom_affiliate_url"] = new_url
            corrected += 1
            
    # Garantia de Monetização: Remove produtos que não possuem link de afiliado válido (ML ou Amazon)
    final_products = []
    for p in products:
        url = p.get("custom_affiliate_url", "")
        if "mercadolivre.com.br" in url and "matt_tool=" in url:
            final_products.append(p)
        elif "amazon.com.br" in url and "tag=" in url:
            final_products.append(p)
        else:
            logger.warning(f"🚫 Produto removido por falta de monetização: {p.get('name', 'Sem Nome')}")

    logger.info(f"✅ Links de afiliado processados: {corrected} correções. {len(final_products)} produtos mantidos com monetização garantida.")
    
    with open(output_p, "w", encoding="utf-8") as f:
        json.dump(final_products, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Processar o banco de dados principal
    process("data/database/all_products.json", "data/database/all_products.json")
    # Também processar arquivos temporários se existirem
    if os.path.exists("data/scored_products.json"):
        process("data/scored_products.json", "data/affiliate_products.json")
