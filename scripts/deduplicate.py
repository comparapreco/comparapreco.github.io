import json
import os
from typing import Any, Dict, List

from logger import logger
from quality_utils import as_float, clean_url, normalize_product, product_signature

DB_FILE = "data/database/all_products.json"
REPORT_FILE = "data/audit_duplicates_report.json"


def _score(product: Dict[str, Any]) -> float:
    return (
        float(product.get("quality_score") or 0) * 2
        + float(product.get("custom_discount_pct") or 0)
        + min(as_float(product.get("price")) / 1000, 10)
    )


def _identity_keys(product: Dict[str, Any]) -> List[str]:
    keys = []
    p_id = product.get("id")
    if p_id:
        keys.append(f"id:{p_id}")
    for field in ("permalink", "custom_affiliate_url"):
        url = clean_url(product.get(field))
        if url:
            keys.append(f"url:{url.split('?')[0].rstrip('/')}")
    keys.append(f"sig:{product_signature(product)}")
    return keys


def deduplicate() -> None:
    if not os.path.exists(DB_FILE):
        logger.warning(f"Banco não encontrado para deduplicação: {DB_FILE}")
        return

    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    winners: Dict[str, Dict[str, Any]] = {}
    key_to_master: Dict[str, str] = {}
    duplicates = []

    for raw in data:
        if not isinstance(raw, dict):
            continue
        product = normalize_product(raw)
        keys = _identity_keys(product)
        master = next((key_to_master[k] for k in keys if k in key_to_master), None)

        if master is None:
            master = keys[0]
            winners[master] = product
            for key in keys:
                key_to_master[key] = master
            continue

        current = winners[master]
        if _score(product) > _score(current):
            duplicates.append({"kept": product.get("id"), "removed": current.get("id"), "reason": "higher_score"})
            winners[master] = product
        else:
            duplicates.append({"kept": current.get("id"), "removed": product.get("id"), "reason": "duplicate_identity"})
        for key in keys:
            key_to_master[key] = master

    final = list(winners.values())
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump({"before": len(data), "after": len(final), "removed": len(data) - len(final), "duplicates": duplicates[:500]}, f, ensure_ascii=False, indent=2)

    logger.info(f"Deduplicação avançada: {len(data)} -> {len(final)} produtos; removidos {len(data) - len(final)}.")


if __name__ == "__main__":
    deduplicate()
