import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from quality_utils import has_bad_public_artifact, product_signature

ROOT = Path(__file__).resolve().parents[1]
DB_FILE = ROOT / "data" / "database" / "all_products.json"
REPORT_FILE = ROOT / "data" / "health" / "advanced_report.json"


def _load_products() -> List[Dict[str, Any]]:
    if not DB_FILE.exists():
        return []
    with DB_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [p for p in data if isinstance(p, dict)]


def _count_public_artifacts() -> Dict[str, int]:
    counters = {"html_with_u002f": 0, "html_with_timestamp_titles": 0, "post_links_with_mlb_timestamp": 0}
    paths = [ROOT / "index.html"]
    posts_dir = ROOT / "noticias" / "posts"
    if posts_dir.exists():
        paths.extend(posts_dir.glob("*.html"))
    for path in paths:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        lower = content.lower()
        visible_text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", content, flags=re.I)
        visible_text = re.sub(r"<[^>]+>", " ", visible_text)
        # Artefatos reais: escapes em texto/URLs internas, IDs técnicos ou timestamps de 14 dígitos expostos em títulos.
        if re.search(r'href=["\'][^"\']*u002f', content, flags=re.I) or "u002f" in visible_text.lower():
            counters["html_with_u002f"] += 1
        if re.search(r'href=["\'][^"\']*MLB\d+[^"\']*\d{14}', content, flags=re.I):
            counters["post_links_with_mlb_timestamp"] += 1
        if re.search(r"<(?:title|h1|h2|h3)[^>]*>[^<]*(?:MLB\d{5,}|\d{14}|u002f)", content, flags=re.I):
            counters["html_with_timestamp_titles"] += 1
    return counters


def build_report() -> Dict[str, Any]:
    products = _load_products()
    signatures = {}
    bad_names = []
    missing_images = 0
    missing_links = 0

    for product in products:
        sig = product_signature(product)
        signatures[sig] = signatures.get(sig, 0) + 1
        if has_bad_public_artifact(product.get("name") or product.get("title")):
            bad_names.append({"id": product.get("id"), "name": product.get("name") or product.get("title")})
        if not (product.get("image") or product.get("thumbnail")):
            missing_images += 1
        if not (product.get("custom_affiliate_url") or product.get("permalink")):
            missing_links += 1

    duplicate_signatures = {k: v for k, v in signatures.items() if v > 1}
    public_artifacts = _count_public_artifacts()

    status = "OK"
    issues = []
    if bad_names:
        status = "WARN"
        issues.append(f"{len(bad_names)} produtos com artefatos técnicos no nome")
    if duplicate_signatures:
        status = "WARN"
        issues.append(f"{len(duplicate_signatures)} assinaturas possivelmente duplicadas")
    if missing_images or missing_links:
        status = "WARN"
        issues.append(f"{missing_images} sem imagem; {missing_links} sem link")
    if any(public_artifacts.values()):
        status = "WARN"
        issues.append(f"artefatos públicos detectados: {public_artifacts}")

    report = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "total_products": len(products),
        "issues": issues,
        "metrics": {
            "bad_names": len(bad_names),
            "duplicate_signatures": len(duplicate_signatures),
            "missing_images": missing_images,
            "missing_links": missing_links,
            "public_artifacts": public_artifacts,
        },
        "samples": {
            "bad_names": bad_names[:20],
            "duplicate_signatures": list(duplicate_signatures.items())[:20],
        },
    }
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_FILE.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return report


if __name__ == "__main__":
    result = build_report()
    print(json.dumps(result, ensure_ascii=False, indent=2))
