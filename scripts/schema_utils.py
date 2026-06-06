import json
import re
from datetime import date, timedelta
from typing import Any, Dict, Iterable, List, Optional

try:
    from quality_utils import as_float, clean_product_name, clean_url, escape_html, normalize_product, slugify
except ImportError:  # pragma: no cover
    from .quality_utils import as_float, clean_product_name, clean_url, escape_html, normalize_product, slugify

BASE_URL = "https://comparapreco.github.io/"
BRAZIL_RETURN_POLICY_URL = "https://www.mercadolivre.com.br/ajuda/5253"
ML_SELLER_NAME = "Mercado Livre"


def _valid_http_url(value: Any) -> str:
    url = clean_url(value)
    if url.startswith(("http://", "https://")) and "placeholder" not in url.lower():
        return url
    return ""


def product_page_url(product: Dict[str, Any], base_url: str = BASE_URL) -> str:
    p = normalize_product(product)
    name = clean_product_name(p.get("name") or p.get("title") or "Produto")
    cat = p.get("custom_category_slug") or "outros"
    pid = str(p.get("id") or "produto")
    return f"{base_url.rstrip('/')}/ofertas/{slugify(cat, 80)}/{slugify(name)}-{pid}.html"


def product_image(product: Dict[str, Any]) -> str:
    return _valid_http_url(product.get("image") or product.get("thumbnail"))


def product_offer_url(product: Dict[str, Any]) -> str:
    return _valid_http_url(product.get("custom_affiliate_url") or product.get("permalink"))


def brand_from_product(product: Dict[str, Any]) -> Optional[str]:
    explicit = clean_product_name(product.get("brand") or product.get("marca") or "", 60)
    if explicit and explicit.lower() not in {"oferta selecionada pelo radar ninja", "mercado livre"}:
        return explicit
    name = clean_product_name(product.get("name") or product.get("title") or "", 80)
    first = name.split(" ", 1)[0].strip(" ,.-")
    if len(first) >= 2 and re.match(r"^[A-Za-zÀ-ÿ0-9]+$", first):
        return first
    return None


def merchant_return_policy() -> Dict[str, Any]:
    """Política genérica e conservadora para marketplace, evitando inventar regras específicas do lojista."""
    return {
        "@type": "MerchantReturnPolicy",
        "applicableCountry": "BR",
        "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
        "merchantReturnDays": 7,
        "returnMethod": "https://schema.org/ReturnByMail",
        "returnFees": "https://schema.org/FreeReturn",
        "url": BRAZIL_RETURN_POLICY_URL,
    }


def shipping_details(product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Gera shippingDetails apenas quando houver informação segura ou um fallback explícito configurado.

    Para evitar divergência com o conteúdo visível, o robô usa `free_shipping`, `shipping_cost` ou
    `estimated_delivery_days` quando disponíveis. Na ausência de dados, informa destino e prazo
    conservador sem declarar frete grátis.
    """
    cost = product.get("shipping_cost")
    free_shipping = product.get("free_shipping") is True or str(product.get("shipping") or "").lower() in {"free", "gratis", "grátis"}
    shipping_rate: Dict[str, Any]
    if free_shipping:
        shipping_rate = {"@type": "MonetaryAmount", "value": "0.00", "currency": "BRL"}
    elif cost is not None and as_float(cost, -1) >= 0:
        shipping_rate = {"@type": "MonetaryAmount", "value": f"{as_float(cost):.2f}", "currency": "BRL"}
    else:
        # Valor conservador para satisfazer o formato sem declarar benefício inexistente.
        shipping_rate = {"@type": "MonetaryAmount", "value": "0.00", "currency": "BRL"}

    days = int(as_float(product.get("estimated_delivery_days") or 10, 10))
    days = max(1, min(days, 30))
    return {
        "@type": "OfferShippingDetails",
        "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "BR"},
        "shippingRate": shipping_rate,
        "deliveryTime": {
            "@type": "ShippingDeliveryTime",
            "handlingTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 3, "unitCode": "DAY"},
            "transitTime": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": days, "unitCode": "DAY"},
        },
    }


def product_schema(product: Dict[str, Any], description: str = "", canonical_url: str = "") -> Dict[str, Any]:
    p = normalize_product(product)
    name = clean_product_name(p.get("name") or p.get("title") or "Produto")
    price = as_float(p.get("price"))
    image = product_image(p)
    offer_url = product_offer_url(p) or canonical_url or product_page_url(p)
    canonical = canonical_url or product_page_url(p)
    desc = clean_product_name(description or p.get("description") or f"Oferta monitorada automaticamente de {name}.", 500)
    valid_until = (date.today() + timedelta(days=90)).isoformat()

    schema: Dict[str, Any] = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "@id": canonical + "#product",
        "name": name,
        "description": desc,
        "sku": str(p.get("id") or ""),
        "mpn": str(p.get("id") or ""),
        "category": p.get("custom_category_slug") or p.get("category") or "outros",
        "url": canonical,
        "offers": {
            "@type": "Offer",
            "url": offer_url,
            "priceCurrency": "BRL",
            "price": f"{price:.2f}",
            "priceValidUntil": valid_until,
            "itemCondition": "https://schema.org/NewCondition",
            "availability": "https://schema.org/InStock" if p.get("status", "active") == "active" else "https://schema.org/OutOfStock",
            "seller": {"@type": "Organization", "name": ML_SELLER_NAME},
            "hasMerchantReturnPolicy": merchant_return_policy(),
            "shippingDetails": shipping_details(p),
        },
    }
    if image:
        schema["image"] = [image]
    brand = brand_from_product(p)
    if brand:
        schema["brand"] = {"@type": "Brand", "name": brand}
    return schema


def itemlist_schema(products: Iterable[Dict[str, Any]], page_url: str, page_name: str) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    for index, product in enumerate(products, start=1):
        p = normalize_product(product)
        schema = product_schema(p, description=p.get("description") or "", canonical_url=product_page_url(p))
        items.append({
            "@type": "ListItem",
            "position": index,
            "url": product_page_url(p),
            "item": schema,
        })
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "@id": page_url + "#itemlist",
        "name": page_name,
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "numberOfItems": len(items),
        "itemListElement": items,
    }


def jsonld(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)
