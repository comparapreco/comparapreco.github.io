import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from quality_utils import as_float, clean_product_name, normalize_product, product_signature
from validate_products import extract_mlb

ROOT = Path(__file__).resolve().parent.parent
DATA_FILES = [
    ROOT / "data/database/all_products.json",
    ROOT / "data/products/offers.json",
    ROOT / "data/new_offers.json",
]


def _name_key(product: Dict[str, Any]) -> Tuple[str, str]:
    name = clean_product_name(product.get("name") or product.get("title") or "", 180).lower()
    name = re.sub(r"\W+", " ", name).strip()
    return str(product.get("custom_category_slug") or "outros"), name


def _score(product: Dict[str, Any]) -> float:
    return as_float(product.get("custom_discount_pct")) * 1000 + max(0, 100000 - as_float(product.get("price")))


def dedupe_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"file": str(path.relative_to(ROOT)), "skipped": True}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return {"file": str(path.relative_to(ROOT)), "skipped": True}

    winners: Dict[str, Dict[str, Any]] = {}
    duplicate_count = 0
    for raw in data:
        if not isinstance(raw, dict):
            continue
        product = normalize_product(raw)
        pid = extract_mlb(product.get("id")) or str(product.get("id") or "").strip()
        key = pid or product_signature(product)
        current = winners.get(key)
        if current is None or _score(product) > _score(current):
            if current is not None:
                duplicate_count += 1
            winners[key] = product
        else:
            duplicate_count += 1

    by_name: Dict[Tuple[str, str], Dict[str, Any]] = {}
    near_duplicate_count = 0
    for product in winners.values():
        key = _name_key(product)
        current = by_name.get(key)
        if current is None or _score(product) > _score(current):
            if current is not None:
                near_duplicate_count += 1
            by_name[key] = product
        else:
            near_duplicate_count += 1

    # Se a mesma imagem externa é usada por nomes claramente diferentes, mantém apenas o melhor item.
    by_image = defaultdict(list)
    for product in by_name.values():
        image = str(product.get("image") or product.get("thumbnail") or "").strip()
        if image:
            by_image[image].append(product)

    final: List[Dict[str, Any]] = []
    image_duplicate_count = 0
    for image, products in by_image.items():
        if len(products) == 1:
            final.append(products[0])
            continue
        normalized_names = {_name_key(p)[1] for p in products}
        if len(normalized_names) == 1:
            final.extend(products)
            continue
        products.sort(key=_score, reverse=True)
        final.append(products[0])
        image_duplicate_count += len(products) - 1

    final.sort(key=lambda p: (str(p.get("custom_category_slug") or "outros"), clean_product_name(p.get("name") or p.get("title") or "")))
    path.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "file": str(path.relative_to(ROOT)),
        "before": len(data),
        "after": len(final),
        "duplicate_ids_removed": duplicate_count,
        "near_duplicate_names_removed": near_duplicate_count,
        "shared_image_suspects_removed": image_duplicate_count,
    }


def main() -> None:
    report = [dedupe_file(path) for path in DATA_FILES]
    out = ROOT / "data/dedupe_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
