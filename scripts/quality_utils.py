import html
import re
import unicodedata
from typing import Any, Dict
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TECHNICAL_TOKEN_RE = re.compile(
    r"\b(?:MLB\d{5,}|AMZ-[A-Z0-9]{6,}|\d{14}|\d{8,}|[a-f0-9]{24,})\b",
    re.IGNORECASE,
)
NOISE_WORDS_RE = re.compile(
    r"\b(?:undefined|null|none|nan|produto|produto-produto|fi)\b",
    re.IGNORECASE,
)
MULTISPACE_RE = re.compile(r"\s+")
DASH_RE = re.compile(r"[-_]{2,}")


def decode_text(value: Any) -> str:
    """Normaliza textos capturados de páginas externas sem confiar no formato de origem."""
    text = "" if value is None else str(value)
    text = html.unescape(text)
    text = text.replace("\\u002F", "/").replace("\\/", "/")
    text = text.replace("u002f", "/").replace("U002F", "/")
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)
    text = text.replace("\xa0", " ")
    return MULTISPACE_RE.sub(" ", text).strip()


def clean_product_name(value: Any, max_len: int = 115) -> str:
    """Remove artefatos técnicos e mantém um título de produto legível para exibição."""
    text = decode_text(value)
    text = TECHNICAL_TOKEN_RE.sub(" ", text)
    text = re.sub(r"\b(?:MLB|AMZ)\b", " ", text, flags=re.IGNORECASE)
    text = NOISE_WORDS_RE.sub(" ", text)
    text = re.sub(r"\s+[/-]\s+", " / ", text)
    text = re.sub(r"\s*,\s*", ", ", text)
    text = DASH_RE.sub("-", text)
    text = MULTISPACE_RE.sub(" ", text).strip(" -_|,.")
    if len(text) > max_len:
        text = text[:max_len].rsplit(" ", 1)[0].strip(" -_|,.")
    return text or "Oferta selecionada pelo Radar Ninja"


def title_from_html(content: str, fallback: str) -> str:
    """Extrai o título editorial real de um HTML já gerado, com limpeza defensiva."""
    for pattern in (r"<h1[^>]*>(.*?)</h1>", r"<title[^>]*>(.*?)</title>"):
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            raw = re.sub(r"<[^>]+>", " ", match.group(1))
            raw = re.sub(r"\s*\|\s*(?:Compara Preço|Radar Ninja).*$", "", raw, flags=re.IGNORECASE)
            raw = re.sub(r"^Análise:\s*", "", raw, flags=re.IGNORECASE)
            cleaned = clean_product_name(raw, 95)
            if cleaned:
                return cleaned
    return clean_product_name(fallback, 95)


def slugify(value: Any, max_len: int = 200) -> str:
    text = clean_product_name(value, max_len=160)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    # Substituir explicitamente "/" por "-" para evitar que o slug remova a barra sem colocar nada no lugar
    text = text.lower().replace("/", "-")
    # Remover pontos explicitamente para evitar 5.3 -> 5-3 ou 53 inconsistente
    text = text.replace(".", "")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    text = re.sub(r"-+", "-", text)
    if len(text) > max_len:
        text = text[:max_len].rsplit("-", 1)[0].strip("-")
    return text or "oferta-radar-ninja"


def escape_attr(value: Any) -> str:
    return html.escape(decode_text(value), quote=True)


def escape_html(value: Any) -> str:
    return html.escape(decode_text(value), quote=False)


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace("R$", "").replace(".", "").replace(",", ".") if isinstance(value, str) and "," in value else value)
    except (TypeError, ValueError):
        return default


def money(value: Any) -> str:
    number = as_float(value)
    if number <= 0:
        return "Preço indisponível"
    return f"R$ {number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def clean_url(url: Any) -> str:
    text = decode_text(url)
    if not text.startswith(("http://", "https://")):
        return ""
    try:
        parts = urlsplit(text)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        ordered_query = urlencode(query, doseq=True)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, ordered_query, ""))
    except Exception:
        return text.split("#", 1)[0]


def product_signature(product: Dict[str, Any]) -> str:
    name = slugify(product.get("name") or product.get("title") or "", 80)
    name = re.sub(r"\b(?:preto|branco|azul|verde|vermelho|cinza|bivolt|127v|220v)\b", "", name)
    name = re.sub(r"-+", "-", name).strip("-")
    price_bucket = int(as_float(product.get("price")) // 10) * 10
    category = product.get("custom_category_slug") or "outros"
    return f"{category}:{name[:70]}:{price_bucket}"


def has_bad_public_artifact(value: Any) -> bool:
    text = decode_text(value)
    if not text:
        return True
    if TECHNICAL_TOKEN_RE.search(text):
        return True
    if "u002f" in text.lower() or "undefined" in text.lower():
        return True
    return False


def normalize_product(product: Dict[str, Any]) -> Dict[str, Any]:
    p = dict(product)
    name = clean_product_name(p.get("name") or p.get("title"))
    p["name"] = name
    p["title"] = name
    if "permalink" in p:
        p["permalink"] = clean_url(p.get("permalink"))
    if "custom_affiliate_url" in p:
        p["custom_affiliate_url"] = clean_url(p.get("custom_affiliate_url"))
    if "image" in p:
        p["image"] = clean_url(p.get("image")) or decode_text(p.get("image"))
    if "thumbnail" in p:
        p["thumbnail"] = clean_url(p.get("thumbnail")) or decode_text(p.get("thumbnail"))
    if not p.get("originalPrice") and p.get("original_price"):
        p["originalPrice"] = p.get("original_price")
    if not p.get("original_price") and p.get("originalPrice"):
        p["original_price"] = p.get("originalPrice")
    try:
        discount = int(float(p.get("custom_discount_pct") or 0))
    except (TypeError, ValueError):
        discount = 0
    p["custom_discount_pct"] = max(0, min(95, discount))
    return p
