#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
errors = []
for html_path in ROOT.rglob('*.html'):
    if '.git' in html_path.parts or 'templates' in html_path.parts:
        continue
    rel = html_path.relative_to(ROOT)
    soup = BeautifulSoup(html_path.read_text(encoding='utf-8', errors='ignore'), 'html.parser')
    attrs = []
    for tag in soup.find_all(['script', 'link', 'img']):
        value = tag.get('src') or tag.get('href')
        if not value or value.startswith(('http://', 'https://', 'mailto:', '#', 'data:', 'tel:')):
            continue
        if value.endswith('/') or value.startswith('./') or value.startswith('../') or not value.startswith('/'):
            clean = value.split('?')[0].split('#')[0]
            if clean.endswith('/'):
                candidate = (html_path.parent / clean / 'index.html').resolve()
            else:
                candidate = (html_path.parent / clean).resolve()
            try:
                candidate.relative_to(ROOT)
            except ValueError:
                continue
            if not candidate.exists():
                errors.append(f'{rel}: referência ausente {value} -> {candidate.relative_to(ROOT)}')

if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print('Validação de assets locais concluída sem referências ausentes.')
