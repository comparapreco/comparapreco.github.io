#!/usr/bin/env python3
"""
Auditoria local de qualidade estática para GitHub Pages.
Verifica links internos quebrados em arquivos HTML e imagens ausentes/quebradas em HTML/JSON de produtos.
"""
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
IGNORE_DIRS = {'.git', '.github', 'node_modules', '__pycache__'}
REPORT = ROOT / 'data' / 'quality_static_audit.json'

INTERNAL_HOSTS = {'comparapreco.github.io', ''}
IMAGE_PLACEHOLDER_PATTERNS = ('placeholder', 'no-image', 'sem-imagem', 'data:image/svg')


def iter_html_files():
    for path in ROOT.rglob('*.html'):
        if any(part in IGNORE_DIRS for part in path.relative_to(ROOT).parts):
            continue
        yield path


def strip_base_url(url: str) -> str | None:
    url = (url or '').strip()
    if not url or url.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'whatsapp:')):
        return None
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc not in INTERNAL_HOSTS:
        return None
    if parsed.netloc and parsed.netloc not in INTERNAL_HOSTS:
        return None
    path = parsed.path if parsed.scheme or parsed.netloc else url.split('#', 1)[0].split('?', 1)[0]
    path = unquote(path)
    if not path:
        return None
    return path


def resolve_link(source: Path, href: str) -> Path | None:
    stripped = strip_base_url(href)
    if stripped is None:
        return None
    if stripped.startswith('/'):
        target = ROOT / stripped.lstrip('/')
    else:
        target = source.parent / stripped
    return target


def page_exists(target: Path) -> bool:
    if target.exists() and target.is_file():
        return True
    if target.exists() and target.is_dir() and (target / 'index.html').exists():
        return True
    if not target.suffix and (target / 'index.html').exists():
        return True
    if not target.suffix and target.with_suffix('.html').exists():
        return True
    return False


def is_bad_image_value(value: str | None) -> bool:
    if not value:
        return True
    v = str(value).strip()
    if not v:
        return True
    low = v.lower()
    return any(p in low for p in IMAGE_PLACEHOLDER_PATTERNS)


def image_exists_or_remote(source: Path, src: str) -> bool:
    if is_bad_image_value(src):
        return False
    parsed = urlparse(src)
    if parsed.scheme in {'http', 'https'}:
        return True
    if src.startswith('/'):
        target = ROOT / src.lstrip('/')
    else:
        target = source.parent / src.split('#', 1)[0].split('?', 1)[0]
    return target.exists()


def audit_html():
    broken_links = []
    bad_images = []
    for html in iter_html_files():
        rel = str(html.relative_to(ROOT))
        try:
            soup = BeautifulSoup(html.read_text(encoding='utf-8', errors='ignore'), 'html.parser')
        except Exception as exc:
            broken_links.append({'file': rel, 'href': '', 'reason': f'erro leitura: {exc}'})
            continue
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            target = resolve_link(html, href)
            if target is not None and not page_exists(target):
                broken_links.append({'file': rel, 'href': href, 'resolved': str(target.relative_to(ROOT)) if str(target).startswith(str(ROOT)) else str(target), 'text': a.get_text(' ', strip=True)[:120]})
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if not image_exists_or_remote(html, src):
                bad_images.append({'file': rel, 'src': src or '', 'alt': img.get('alt', '')[:120]})
    return broken_links, bad_images


def audit_product_json():
    json_files = [
        'data/raw_products.json',
        'data/scored_products.json',
        'data/affiliate_products.json',
        'data/database/all_products.json',
        'data/products/offers.json',
    ]
    bad = []
    counts = {}
    for rel in json_files:
        path = ROOT / rel
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except Exception as exc:
            bad.append({'file': rel, 'id': '', 'name': '', 'reason': f'erro JSON: {exc}'})
            continue
        if isinstance(data, dict):
            # tenta encontrar lista principal
            if isinstance(data.get('products'), list):
                items = data['products']
            elif isinstance(data.get('offers'), list):
                items = data['offers']
            else:
                items = []
        elif isinstance(data, list):
            items = data
        else:
            items = []
        total = len(items)
        missing = 0
        for p in items:
            if not isinstance(p, dict):
                continue
            image = p.get('image') or p.get('thumbnail') or p.get('image_url') or p.get('picture')
            if is_bad_image_value(image):
                missing += 1
                bad.append({'file': rel, 'id': p.get('id', ''), 'name': p.get('name') or p.get('title', ''), 'image': image or ''})
        counts[rel] = {'total': total, 'bad_images': missing}
    return counts, bad


def main():
    broken_links, bad_html_images = audit_html()
    product_counts, bad_product_images = audit_product_json()
    report = {
        'summary': {
            'html_files': sum(1 for _ in iter_html_files()),
            'broken_internal_links': len(broken_links),
            'bad_html_images': len(bad_html_images),
            'bad_product_json_images': len(bad_product_images),
        },
        'product_json_counts': product_counts,
        'broken_internal_links': broken_links[:500],
        'bad_html_images': bad_html_images[:500],
        'bad_product_json_images': bad_product_images[:500],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report['summary'], ensure_ascii=False, indent=2))
    for key, value in product_counts.items():
        print(key, value)
    print(f'Relatório: {REPORT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
