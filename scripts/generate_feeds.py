import html
import re
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Dict, List
from xml.sax.saxutils import escape

from logger import logger

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://comparapreco.github.io/"
POSTS_DIR = ROOT / "noticias" / "posts"
RSS_FILE = ROOT / "feed.xml"
ATOM_FILE = ROOT / "atom.xml"


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "")


def extract(pattern: str, content: str, default: str = "") -> str:
    match = re.search(pattern, content, flags=re.IGNORECASE | re.DOTALL)
    return html.unescape(match.group(1).strip()) if match else default


def collect_posts(limit: int = 30) -> List[Dict[str, str]]:
    if not POSTS_DIR.exists():
        return []
    posts = sorted(POSTS_DIR.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    items: List[Dict[str, str]] = []
    for post in posts:
        content = post.read_text(encoding="utf-8", errors="ignore")
        title = extract(r"<title>(.*?)\s*\|\s*Compara Preço</title>", content) or extract(r"<h1[^>]*>(.*?)</h1>", content, post.stem)
        description = extract(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content)
        if not description:
            first_paragraph = extract(r"<p[^>]*>(.*?)</p>", content, title)
            description = strip_tags(first_paragraph).strip()[:240]
        updated = datetime.fromtimestamp(post.stat().st_mtime, timezone.utc)
        rel = post.relative_to(ROOT).as_posix()
        items.append({
            "title": title,
            "description": description,
            "url": f"{BASE_URL}{rel}",
            "updated_iso": updated.isoformat().replace("+00:00", "Z"),
            "updated_rfc": format_datetime(updated),
        })
    return items


def generate_rss(items: List[Dict[str, str]]) -> None:
    now = format_datetime(datetime.now(timezone.utc))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0">',
        '  <channel>',
        '    <title>Compara Preço - Notícias e Ofertas</title>',
        f'    <link>{BASE_URL}</link>',
        '    <description>Análises automáticas de ofertas monitoradas pelo Radar Ninja.</description>',
        f'    <lastBuildDate>{now}</lastBuildDate>',
        '    <language>pt-BR</language>',
    ]
    for item in items:
        lines.extend([
            '    <item>',
            f'      <title>{escape(item["title"])}</title>',
            f'      <link>{escape(item["url"])}</link>',
            f'      <guid isPermaLink="true">{escape(item["url"])}</guid>',
            f'      <pubDate>{item["updated_rfc"]}</pubDate>',
            f'      <description>{escape(item["description"])}</description>',
            '    </item>',
        ])
    lines.extend(['  </channel>', '</rss>', ''])
    RSS_FILE.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Feed RSS atualizado: {RSS_FILE.relative_to(ROOT)} com {len(items)} itens")


def generate_atom(items: List[Dict[str, str]]) -> None:
    updated = items[0]["updated_iso"] if items else datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom">',
        '  <title>Compara Preço - Notícias e Ofertas</title>',
        f'  <link href="{BASE_URL}"/>',
        f'  <link rel="self" href="{BASE_URL}atom.xml"/>',
        f'  <id>{BASE_URL}</id>',
        f'  <updated>{updated}</updated>',
    ]
    for item in items:
        lines.extend([
            '  <entry>',
            f'    <title>{escape(item["title"])}</title>',
            f'    <link href="{escape(item["url"])}"/>',
            f'    <id>{escape(item["url"])}</id>',
            f'    <updated>{item["updated_iso"]}</updated>',
            f'    <summary>{escape(item["description"])}</summary>',
            '  </entry>',
        ])
    lines.extend(['</feed>', ''])
    ATOM_FILE.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Feed Atom atualizado: {ATOM_FILE.relative_to(ROOT)} com {len(items)} itens")


def main() -> None:
    items = collect_posts()
    generate_rss(items)
    generate_atom(items)


if __name__ == "__main__":
    main()
