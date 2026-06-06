import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_OFFER_FIELDS = {"price", "priceCurrency", "availability", "url", "itemCondition", "hasMerchantReturnPolicy", "shippingDetails"}
REQUIRED_PRODUCT_FIELDS = {"name", "image", "description", "sku", "offers"}


def _load_jsonld_blocks(html: str) -> List[Any]:
    soup = BeautifulSoup(html, "html.parser")
    blocks: List[Any] = []
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        text = script.string or script.get_text() or ""
        if not text.strip():
            continue
        try:
            blocks.append(json.loads(text))
        except json.JSONDecodeError as exc:
            blocks.append({"__json_error__": str(exc), "__raw__": text[:200]})
    return blocks


def _iter_nodes(obj: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from _iter_nodes(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _iter_nodes(item)


def _visible_price(html: str) -> float:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    match = re.search(r"R\$\s*([0-9\.]+,[0-9]{2})", text)
    if not match:
        return 0.0
    return float(match.group(1).replace(".", "").replace(",", "."))


def _as_float(value: Any) -> float:
    try:
        return float(str(value).replace("R$", "").replace(".", "").replace(",", ".") if "," in str(value) else value)
    except Exception:
        return 0.0


def audit_html_file(path: Path) -> List[str]:
    rel = str(path.relative_to(ROOT))
    html = path.read_text(encoding="utf-8", errors="ignore")
    issues: List[str] = []
    if "MLB123456789" in html:
        issues.append(f"{rel}: contém ID fictício")
    soup_for_assets = BeautifulSoup(html, "html.parser")
    for img in soup_for_assets.find_all("img"):
        src = str(img.get("src") or "").lower()
        if any(token in src for token in ("placeholder", "no-image", "sem-imagem", "via.placeholder")):
            issues.append(f"{rel}: imagem placeholder em {src[:80]}")
            break
    blocks = _load_jsonld_blocks(html)
    if any(isinstance(b, dict) and "__json_error__" in b for b in blocks):
        issues.append(f"{rel}: JSON-LD inválido")
    nodes = [n for block in blocks for n in _iter_nodes(block)]
    products = [n for n in nodes if n.get("@type") == "Product"]
    itemlists = [n for n in nodes if n.get("@type") == "ItemList"]
    if rel.startswith("ofertas/") and path.name != "index.html":
        if not products:
            issues.append(f"{rel}: página de produto sem Product JSON-LD")
        for product in products:
            missing = sorted(field for field in REQUIRED_PRODUCT_FIELDS if not product.get(field))
            if missing:
                issues.append(f"{rel}: Product sem campos {missing}")
            offer = product.get("offers") or {}
            if isinstance(offer, list):
                offer = offer[0] if offer else {}
            missing_offer = sorted(field for field in REQUIRED_OFFER_FIELDS if not offer.get(field))
            if missing_offer:
                issues.append(f"{rel}: Offer sem campos {missing_offer}")
            visible = _visible_price(html)
            schema_price = _as_float(offer.get("price"))
            if visible and schema_price and abs(visible - schema_price) > 0.02:
                issues.append(f"{rel}: preço visível {visible:.2f} diverge do Schema {schema_price:.2f}")
    if rel.startswith("melhores-2026/"):
        if not itemlists:
            issues.append(f"{rel}: ranking sem ItemList JSON-LD")
        soup = BeautifulSoup(html, "html.parser")
        for img in soup.find_all("img"):
            if not img.get("alt"):
                issues.append(f"{rel}: imagem sem alt")
                break
    return issues


def audit_duplicate_products() -> List[str]:
    issues: List[str] = []
    data_files = [ROOT / "data/products/offers.json", ROOT / "data/database/all_products.json"]
    for data_file in data_files:
        if not data_file.exists():
            continue
        data = json.loads(data_file.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            continue
        ids = Counter(str(p.get("id") or "") for p in data if isinstance(p, dict) and p.get("id"))
        duplicate_ids = [pid for pid, count in ids.items() if count > 1]
        if duplicate_ids:
            issues.append(f"{data_file.relative_to(ROOT)}: {len(duplicate_ids)} IDs duplicados; exemplos: {duplicate_ids[:5]}")
        names_by_cat = Counter((str(p.get("custom_category_slug") or "outros"), re.sub(r"\W+", " ", str(p.get("name") or p.get("title") or "").lower()).strip()) for p in data if isinstance(p, dict))
        duplicated_names = [name for name, count in names_by_cat.items() if count > 1 and name[1]]
        if duplicated_names:
            issues.append(f"{data_file.relative_to(ROOT)}: {len(duplicated_names)} nomes duplicados por categoria; exemplos: {duplicated_names[:3]}")
    return issues


def main() -> None:
    issues: List[str] = []
    for folder in [ROOT / "ofertas", ROOT / "melhores-2026"]:
        if not folder.exists():
            continue
        for html_file in folder.rglob("*.html"):
            issues.extend(audit_html_file(html_file))
    issues.extend(audit_duplicate_products())

    report = {
        "ok": not issues,
        "total_issues": len(issues),
        "issues": issues[:1000],
    }
    out = ROOT / "data/quality_gate_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if issues:
        print(f"Quality gate failed with {len(issues)} issue(s). See {out}")
        for issue in issues[:50]:
            print("-", issue)
        raise SystemExit(1)
    print("Quality gate OK: Schema.org, preços, imagens, links e duplicidades básicas validados.")


if __name__ == "__main__":
    main()
