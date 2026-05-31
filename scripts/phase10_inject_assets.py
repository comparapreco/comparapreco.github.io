#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / 'index.html',
    ROOT / 'meus-favoritos' / 'index.html',
    ROOT / 'admin' / 'index.html',
    ROOT / 'admin' / 'login.html',
    ROOT / 'alertas' / 'index.html',
    ROOT / 'imprensa' / 'index.html',
    ROOT / 'parcerias' / 'index.html',
    ROOT / 'midia-kit' / 'index.html',
    ROOT / 'precos-index' / 'index.html',
    ROOT / 'academia' / 'index.html',
    ROOT / 'exclusivos' / 'index.html',
]

EXTRA_DIRS = ['ofertas-hoje', 'quedas-hoje', 'melhores-ofertas', 'mais-clicados']
for directory in EXTRA_DIRS:
    path = ROOT / directory / 'index.html'
    if path.exists():
        TARGETS.append(path)


def prefix_for(path: Path) -> str:
    rel_parent = path.parent.relative_to(ROOT)
    if str(rel_parent) == '.':
        return ''
    depth = len(rel_parent.parts)
    return '../' * depth


def inject_before(html: str, marker: str, snippet: str) -> str:
    if snippet.strip() in html:
        return html
    if marker in html:
        return html.replace(marker, snippet + '\n  ' + marker, 1)
    return html.replace('</body>', snippet + '\n</body>', 1)


def process(path: Path) -> None:
    html = path.read_text(encoding='utf-8')
    prefix = prefix_for(path)

    manifest = f'<link rel="manifest" href="{prefix}manifest.webmanifest">'
    theme = '<meta name="theme-color" content="#00c853">'
    icon = f'<link rel="apple-touch-icon" href="{prefix}assets/icons/icon-192.png">'
    if manifest not in html:
        html = html.replace('</head>', f'  {manifest}\n  {theme}\n  {icon}\n</head>', 1)

    config = f'<script src="{prefix}assets/js/firebase-config.js"></script>'
    auth = f'<script src="{prefix}assets/js/compara-auth.js"></script>'
    pwa = f'<script src="{prefix}assets/js/pwa.js"></script>'
    app_marker = f'<script src="{prefix}assets/js/app.js"></script>'

    html = inject_before(html, app_marker, f'  {config}\n  {auth}\n  {pwa}')

    path.write_text(html, encoding='utf-8')
    print(f'Atualizado: {path.relative_to(ROOT)}')


if __name__ == '__main__':
    for target in TARGETS:
        if target.exists():
            process(target)
