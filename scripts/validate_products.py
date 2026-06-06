import json
import os
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from logger import logger
from quality_utils import as_float, clean_product_name, clean_url, has_bad_public_artifact, normalize_product, product_signature

INPUT_CANDIDATES = [
    "data/new_offers.json",
    "data/affiliate_products.json",
    "data/scored_products.json",
]

BLOCKED_TERMS = {
    "capinha", "pelicula", "película", "usado", "recondicionado", "vitrine",
    "quebrado", "defeito", "ebook", "e-book", "pdf", "curso", "serviço",
    "assinatura", "conta premium", "link de acesso",
}

REQUIRED_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".avif")
AFFILIATE_PARAM = "matt_tool"
AFFILIATE_TAG = "vendas0nline"


def _select_input_file() -> str:
    for path in INPUT_CANDIDATES:
        if os.path.exists(path):
            return path
    return INPUT_CANDIDATES[0]


def extract_mlb(value: Any) -> Optional[str]:
    text = str(value or "")
    match = re.search(r"MLB\d+", text, re.IGNORECASE)
    return match.group(0).upper() if match else None


def _has_affiliate_tag(url: str) -> bool:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params.get(AFFILIATE_PARAM, [None])[0] == AFFILIATE_TAG


def _valid_image_url(url: str) -> bool:
    if not url or not url.startswith(("http://", "https://")):
        return False
    lower = url.lower()
    if any(token in lower for token in ("placeholder", "no-image", "sem-imagem", "undefined", "null")):
        return False
    path = urlparse(url).path.lower()
    return path.endswith(REQUIRED_IMAGE_EXTENSIONS) or "http2.mlstatic.com" in lower or "m.media-amazon.com" in lower


def _looks_like_wrong_image(product: Dict[str, Any]) -> bool:
    """Heurística defensiva para bloquear artefatos visíveis, sem tentar reconhecer imagem por IA."""
    name = clean_product_name(product.get("name") or product.get("title") or "").lower()
    image = str(product.get("image") or product.get("thumbnail") or "").lower()
    if not image:
        return True
    image_id = extract_mlb(image)
    product_id = extract_mlb(product.get("id"))
    if image_id and product_id and image_id != product_id:
        return True
    if "apple" in image and not any(t in name for t in ("apple", "iphone", "ipad", "macbook", "airpods")):
        return True
    return False


def validate_product(product: Dict[str, Any], mutate: bool = True, strict_links: bool = True) -> Tuple[bool, str]:
    """Valida e normaliza um produto antes da publicação.

    A função retorna `(ok, motivo)` e bloqueia: preço inexistente, nome genérico, imagem
    inválida ou provavelmente trocada, URL sem HTTP, divergência entre ID MLB e URL de
    afiliado, links sem tag de afiliado quando `strict_links=True` e artefatos públicos.
    """
    try:
        p = normalize_product(product)
        if mutate:
            product.clear()
            product.update(p)

        pid = str(p.get("id") or "").strip()
        name = clean_product_name(p.get("name") or p.get("title") or "")
        if not pid or not name:
            return False, "sem id ou nome"

        name_lower = name.lower()
        if len(name) < 8 or any(term in name_lower for term in BLOCKED_TERMS):
            return False, "nome bloqueado ou genérico"
        if has_bad_public_artifact(name):
            return False, "artefato técnico no nome"

        price = as_float(p.get("price"))
        if price <= 0:
            return False, "preço inválido ou inexistente"
        p["price"] = round(price, 2)

        original = as_float(p.get("originalPrice") or p.get("original_price"))
        if original and original < price:
            p["originalPrice"] = price
            p["original_price"] = price
            p["custom_discount_pct"] = 0

        url = clean_url(p.get("custom_affiliate_url") or p.get("permalink"))
        if not url:
            return False, "url inválida"
        if strict_links and "mercadolivre" in url and not _has_affiliate_tag(url):
            return False, "url sem tag de afiliado"

        pid_mlb = extract_mlb(pid)
        url_mlb = extract_mlb(url)
        if pid_mlb and url_mlb and pid_mlb != url_mlb:
            return False, f"id divergente da url: {pid_mlb} vs {url_mlb}"

        image = clean_url(p.get("image") or p.get("thumbnail"))
        if not _valid_image_url(image):
            return False, "imagem inválida"
        p["image"] = image
        if not p.get("thumbnail"):
            p["thumbnail"] = image
        if _looks_like_wrong_image(p):
            return False, "imagem possivelmente associada a outro item"

        discount = int(as_float(p.get("custom_discount_pct")))
        p["custom_discount_pct"] = max(0, min(95, discount))
        if not p.get("custom_category_slug"):
            p["custom_category_slug"] = "outros"
        if len(clean_product_name(p.get("description") or "")) < 80:
            p["description"] = (
                f"Oferta monitorada automaticamente para {name}. O Compara Preço valida preço, imagem, link, "
                "disponibilidade e consistência dos dados estruturados antes de publicar esta recomendação."
            )
        if mutate:
            product.clear()
            product.update(p)
        return True, "aprovado"
    except Exception as exc:
        return False, f"erro: {exc}"


def remove_duplicates(products: Iterable[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    winners: Dict[str, Dict[str, Any]] = {}
    rejected = {"duplicado": 0}
    for product in products:
        signature = extract_mlb(product.get("id")) or product_signature(product)
        current = winners.get(signature)
        if current is None:
            winners[signature] = product
            continue
        rejected["duplicado"] += 1
        current_score = as_float(current.get("custom_discount_pct")) * 1000 - as_float(current.get("price"))
        new_score = as_float(product.get("custom_discount_pct")) * 1000 - as_float(product.get("price"))
        if new_score > current_score:
            winners[signature] = product
    return list(winners.values()), rejected


def main() -> None:
    input_file = _select_input_file()
    if not os.path.exists(input_file):
        logger.error("Arquivo de ofertas não encontrado para validação.")
        return

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("arquivo de produtos não contém lista JSON")

        valid_products: List[Dict[str, Any]] = []
        rejected: Dict[str, int] = {}
        for product in data:
            if not isinstance(product, dict):
                rejected["registro inválido"] = rejected.get("registro inválido", 0) + 1
                continue
            ok, reason = validate_product(product)
            if ok:
                valid_products.append(product)
            else:
                rejected[reason] = rejected.get(reason, 0) + 1

        valid_products, dup_rejected = remove_duplicates(valid_products)
        for key, value in dup_rejected.items():
            rejected[key] = rejected.get(key, 0) + value

        if len(valid_products) < 5 and len(data) > 10:
            logger.error("Alerta de sanidade: muitos produtos foram invalidados. Abortando para proteger o site.")
            logger.error(f"Rejeições: {rejected}")
            raise SystemExit(1)

        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(valid_products, f, ensure_ascii=False, indent=2)

        report_path = "data/validation_publication_report.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({"input": input_file, "aprovados": len(valid_products), "rejeitados": rejected}, f, ensure_ascii=False, indent=2)

        logger.info(f"Validação concluída em {input_file}: {len(valid_products)} aprovados, {len(data) - len(valid_products)} rejeitados. Motivos: {rejected}")
    except Exception as exc:
        logger.error(f"Erro na validação de dados: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
