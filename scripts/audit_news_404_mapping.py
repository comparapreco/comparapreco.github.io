import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "noticias" / "index.html"
POSTS = ROOT / "noticias" / "posts"


def extract_news_items():
    text = INDEX.read_text(encoding="utf-8")
    items = []
    for match in re.finditer(r'\{\s*"id"\s*:\s*.*?\n\s*\}', text, flags=re.S):
        block = match.group(0)
        title_m = re.search(r'"title"\s*:\s*"(.*?)"\s*,', block, flags=re.S)
        url_m = re.search(r'"url"\s*:\s*"(.*?)"', block, flags=re.S)
        if title_m and url_m:
            title = bytes(title_m.group(1), "utf-8").decode("unicode_escape")
            url = url_m.group(1)
            items.append({"title": title, "url": url})
    return items


def normalized(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9áàâãéêíóôõúç]+', ' ', s)
    for token in ["analise", "vale", "pena", "comprar", "com", "off", "desconto"]:
        s = re.sub(rf'\b{token}\b', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def post_title(path):
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(" ", strip=True)
    title = soup.find("title")
    return title.get_text(" ", strip=True) if title else path.stem


def main():
    items = extract_news_items()
    existing = []
    for path in POSTS.glob("*.html"):
        existing.append({"path": path, "file": path.name, "title": post_title(path), "norm": normalized(post_title(path) + " " + path.stem)})
    missing = []
    for item in items:
        if item["url"].startswith("posts/") and not (ROOT / "noticias" / item["url"]).exists():
            query = normalized(item["title"] + " " + Path(item["url"]).stem)
            best = sorted(existing, key=lambda e: SequenceMatcher(None, query, e["norm"]).ratio(), reverse=True)[:3]
            missing.append({"title": item["title"], "url": item["url"], "best": [(b["file"], round(SequenceMatcher(None, query, b["norm"]).ratio(), 3), b["title"][:120]) for b in best]})
    print(json.dumps({"total_items": len(items), "missing": len(missing), "missing_items": missing}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
