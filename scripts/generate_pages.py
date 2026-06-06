import json
import os
import random
from typing import Any, Dict, List

from logger import logger
from quality_utils import clean_product_name, escape_attr, escape_html, money, normalize_product, slugify, as_float

BASE_URL = "https://comparapreco.github.io/"


def generate_product_page(product: Dict[str, Any], all_products: List[Dict[str, Any]], template_path: str, output_dir: str) -> None:
    product = normalize_product(product)
    product_name = clean_product_name(product.get("name") or product.get("title") or "Produto")

    if not os.path.exists(template_path):
        logger.error(f"Template não encontrado: {template_path}")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    p_id = str(product.get("id", "0"))
    p_slug = slugify(product_name)
    p_cat_slug = product.get("custom_category_slug", "outros")
    p_status = product.get("status", "active")

    price_val = as_float(product.get("price"))
    orig_val = as_float(product.get("originalPrice") or product.get("original_price"))
    if orig_val < price_val:
        orig_val = price_val

    p_price = money(price_val)
    p_orig = money(orig_val)
    p_img = product.get("image") or product.get("thumbnail") or ""

    p_url = product.get("custom_affiliate_url") or product.get("permalink") or "#"
    p_discount = int(product.get("custom_discount_pct") or 0)

    status_html = ""
    if p_status == "expired":
        status_html = '<div class="status-banner expired">⚠️ Esta oferta pode ter encerrado. Confira produtos similares abaixo.</div>'

    similars = [
        normalize_product(p)
        for p in all_products
        if p.get("custom_category_slug") == p_cat_slug and str(p.get("id")) != p_id and p.get("status", "active") == "active"
    ]
    random.shuffle(similars)
    similars = similars[:4]

    similars_html = ""
    if similars:
        similars_html = '<div class="similar-products"><h2>Produtos similares em oferta</h2><div class="products-grid">'
        for similar in similars:
            s_full_name = clean_product_name(similar.get("name") or similar.get("title"))
            s_name = clean_product_name(s_full_name, 62)
            s_price = money(similar.get("price"))
            s_slug = slugify(s_full_name)
            s_id = similar.get("id", "produto")
            s_url = f"../../ofertas/{similar.get('custom_category_slug', 'outros')}/{s_slug}-{s_id}.html"
            similars_html += f"""
            <div class="product-card">
                <div class="card-img"><img src="{escape_attr(similar.get('image') or similar.get('thumbnail') or '')}" alt="{escape_attr(s_name)}" loading="lazy"></div>
                <h3>{escape_html(s_name)}</h3>
                <div class="price-tag">{s_price}</div>
                <a href="{escape_attr(s_url)}" class="btn">Ver oferta</a>
            </div>
            """
        similars_html += "</div></div>"

    seo_title = f"{product_name} | Compara Preço"
    if p_status == "active" and p_discount:
        seo_title = f"{product_name} com {p_discount}% de desconto | Compara Preço"

    meta_desc = (
        f"Veja preço atualizado, dados da oferta e pontos de atenção sobre {product_name}. "
        "Compare antes de comprar e acompanhe variações do anúncio."
    )
    canonical_url = f"{BASE_URL}ofertas/{p_cat_slug}/{p_slug}-{p_id}.html"

    desc = product.get("description") or (
        f"Oferta monitorada automaticamente pelo Radar Ninja. Confira preço, desconto, disponibilidade e detalhes antes de comprar {product_name}."
    )

    replacements = {
        "{{seo.title}}": escape_html(seo_title),
        "{{meta.description}}": escape_attr(meta_desc),
        "{{canonical.url}}": escape_attr(canonical_url),
        "{{product.status_banner}}": status_html,
        "{{product.similars}}": similars_html,
        "{{product.name}}": escape_html(product_name),
        "{{product.price}}": p_price,
        "{{product.price_raw}}": str(price_val),
        "{{product.originalPrice}}": p_orig,
        "{{product.originalPrice_raw}}": str(orig_val),
        "{{product.image}}": escape_attr(p_img),
        "{{product.url}}": escape_attr(p_url),
        "{{product.id}}": escape_attr(p_id),
        "{{product.category}}": escape_html(p_cat_slug),
        "{{product.discount}}": str(p_discount),
        "{{product.description_content}}": escape_html(desc),
    }

    content = template
    for marker, value in replacements.items():
        content = content.replace(marker, value)

    path = os.path.join(output_dir, p_cat_slug, f"{p_slug}-{p_id}.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _clear_stale_offer_pages(out_d: str) -> int:
    removed = 0
    if not os.path.exists(out_d):
        return removed
    for root, _, files in os.walk(out_d):
        for file_name in files:
            if not file_name.endswith(".html") or file_name == "index.html":
                continue
            path = os.path.join(root, file_name)
            try:
                os.remove(path)
                removed += 1
            except OSError:
                pass
    return removed


def generate_all(input_p: str, temp_p: str, out_d: str) -> None:
    if not os.path.exists(input_p):
        logger.warning(f"Banco não encontrado: {input_p}")
        return
    try:
        with open(input_p, "r", encoding="utf-8") as f:
            all_products = json.load(f)
    except Exception as exc:
        logger.error(f"Erro ao ler banco de dados: {exc}")
        return

    normalized = [normalize_product(p) for p in all_products if isinstance(p, dict)]
    removed = _clear_stale_offer_pages(out_d)
    logger.info(f"Gerando {len(normalized)} páginas permanentes com sanitização avançada... {removed} páginas antigas removidas.")
    for product in normalized:
        generate_product_page(product, normalized, temp_p, out_d)


if __name__ == "__main__":
    generate_all("data/database/all_products.json", "templates/product_template.html", "ofertas")
