import re
from pathlib import Path

from quality_utils import slugify, title_from_html

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "noticias" / "posts"
BASE_URL = "https://comparapreco.github.io/noticias/posts/"
TECHNICAL_SLUG_RE = re.compile(r"(MLB\d{5,}|\d{14})", re.IGNORECASE)


def _unique_path(base: Path) -> Path:
    if not base.exists():
        return base
    counter = 2
    while True:
        candidate = base.with_name(f"{base.stem}-{counter}{base.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def clean_posts() -> int:
    if not POSTS_DIR.exists():
        return 0
    renamed = 0
    for path in sorted(POSTS_DIR.glob("*.html")):
        if not TECHNICAL_SLUG_RE.search(path.name):
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        title = title_from_html(content, path.stem)
        new_name = f"analise-{slugify(title, 72)}.html"
        new_path = _unique_path(path.with_name(new_name))
        new_url = BASE_URL + new_path.name
        content = re.sub(r"https://comparapreco\.github\.io/noticias/posts/[^\"'<\s]+\.html", new_url, content)
        new_path.write_text(content, encoding="utf-8")
        path.unlink()
        renamed += 1
    print(f"Posts legados renomeados: {renamed}")
    return renamed


if __name__ == "__main__":
    clean_posts()
