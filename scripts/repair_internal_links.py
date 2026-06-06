import json
import os
import re
from pathlib import Path

from quality_utils import clean_product_name, slugify

ROOT = Path(__file__).resolve().parents[1]
DB_FILE = ROOT / "data" / "database" / "all_products.json"
ID_RE = re.compile(r"(MLB\d+|AMZ-[A-Z0-9]+)")
HREF_RE = re.compile(r'href="([^"]*ofertas/[^"]*?(?:MLB\d+|AMZ-[A-Z0-9]+)\.html)"')
SKIP_DIRS = {".git", "templates", "node_modules", "__pycache__"}


def _load_map():
    if not DB_FILE.exists():
        return {}
    data = json.loads(DB_FILE.read_text(encoding="utf-8"))
    mapping = {}
    for product in data:
        if not isinstance(product, dict) or not product.get("id"):
            continue
        p_id = str(product.get("id"))
        name = clean_product_name(product.get("name") or product.get("title"))
        cat = product.get("custom_category_slug") or "outros"
        mapping[p_id] = ROOT / "ofertas" / cat / f"{slugify(name)}-{p_id}.html"
    return mapping


def _iter_html_files():
    for path in ROOT.rglob("*.html"):
        rel_parts = path.relative_to(ROOT).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        yield path


def _relative_href(from_file: Path, target: Path) -> str:
    rel = os.path.relpath(target, from_file.parent).replace(os.sep, "/")
    if not rel.startswith("."):
        rel = "./" + rel
    return rel


def repair_links() -> int:
    mapping = _load_map()
    changed_files = 0
    for path in _iter_html_files():
        original = path.read_text(encoding="utf-8", errors="ignore")

        def replace(match):
            href = match.group(1)
            id_match = ID_RE.search(href)
            if not id_match:
                return match.group(0)
            target = mapping.get(id_match.group(1))
            if not target or not target.exists():
                return match.group(0)
            clean_href = _relative_href(path, target)
            return f'href="{clean_href}"'

        updated = HREF_RE.sub(replace, original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed_files += 1
    print(f"Arquivos com links internos reparados: {changed_files}")
    return changed_files


if __name__ == "__main__":
    repair_links()
