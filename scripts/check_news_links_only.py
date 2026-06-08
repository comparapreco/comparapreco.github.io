import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEWS_DIR = ROOT / "noticias"

broken = []
checked = 0
for html_file in NEWS_DIR.glob("**/*.html"):
    content = html_file.read_text(encoding="utf-8", errors="ignore")
    for link in re.findall(r'(?:href|url)=["\']([^"\']+\.html)["\']|"url"\s*:\s*"([^"]+\.html)"', content):
        href = link[0] or link[1]
        if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            continue
        checked += 1
        if href.startswith("/"):
            target = ROOT / href.lstrip("/")
        else:
            target = (html_file.parent / href).resolve()
        try:
            target.relative_to(ROOT)
        except ValueError:
            continue
        if not target.exists():
            broken.append((html_file.relative_to(ROOT).as_posix(), href, target.relative_to(ROOT).as_posix()))

print(f"links_verificados={checked}")
print(f"links_quebrados={len(broken)}")
for source, href, target in broken[:50]:
    print(f"{source} -> {href} -> {target}")
