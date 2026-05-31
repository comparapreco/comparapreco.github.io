import os
import json
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse, urljoin
from logger import logger

# ID do afiliado: lido da variável de ambiente, com fallback para 'vendas0nline'
AFILIADO_ID = os.environ.get("ML_AFILIADO_ID", "vendas0nline")


def build_affiliate_url(product: dict) -> str:
    """
    Constrói a URL de afiliado correta para um produto do Mercado Livre.

    Estratégia de prioridade:
    1. Se já existe um custom_affiliate_url válido (aponta para produto, não para /social/),
       mantém-o adicionando o parâmetro de rastreamento do afiliado.
    2. Caso contrário, usa o permalink do produto (campo 'permalink') e adiciona
       o parâmetro 'matt_tool' com o ID do afiliado para rastreamento.
    3. Como último recurso, constrói a URL diretamente via /p/<id>.
    """
    product_id = product.get("id", "")
    permalink = product.get("permalink", "")
    current_affiliate = product.get("custom_affiliate_url", "")

    # Detecta se o custom_affiliate_url atual é inválido (aponta para /social/)
    is_invalid_affiliate = (
        not current_affiliate
        or "/social/" in current_affiliate
        or "vendas0nline/lists" in current_affiliate
        or "vendas0nline?" in current_affiliate
    )

    if not is_invalid_affiliate:
        # URL de afiliado já é válida — apenas garante o parâmetro de rastreamento
        base_url = current_affiliate
    elif permalink:
        # Usa o permalink do produto (URL canônica da página do produto)
        base_url = permalink
    elif product_id:
        # Fallback: constrói via /p/<id>
        base_url = f"https://www.mercadolivre.com.br/p/{product_id}"
    else:
        logger.warning(f"Produto sem ID nem permalink: {product.get('name', 'desconhecido')}")
        return ""

    # Adiciona o parâmetro de rastreamento do afiliado (matt_tool)
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params["matt_tool"] = [AFILIADO_ID]

    # Reconstrói a query string preservando parâmetros existentes
    new_query = urlencode({k: v[0] for k, v in params.items()})
    new_url = urlunparse(parsed._replace(query=new_query))

    return new_url


def process(input_p: str, output_p: str):
    if not os.path.exists(input_p):
        logger.warning(f"Arquivo de entrada não encontrado: {input_p}")
        products = []
    else:
        with open(input_p, "r", encoding="utf-8") as f:
            products = json.load(f)

    corrected = 0
    for product in products:
        old_url = product.get("custom_affiliate_url", "")
        new_url = build_affiliate_url(product)
        product["custom_affiliate_url"] = new_url

        if old_url != new_url:
            corrected += 1
            logger.info(
                f"[CORRIGIDO] {product.get('id', '?')} | "
                f"Antes: {old_url[:80]} | "
                f"Depois: {new_url[:80]}"
            )

    logger.info(f"Links corrigidos: {corrected}/{len(products)}")

    os.makedirs(os.path.dirname(output_p) if os.path.dirname(output_p) else ".", exist_ok=True)
    with open(output_p, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    logger.info(f"Arquivo salvo: {output_p}")


if __name__ == "__main__":
    process("data/scored_products.json", "data/affiliate_products.json")
