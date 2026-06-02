#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urldefrag, unquote
from collections import Counter, defaultdict
import json, re, posixpath

ROOT = Path('/home/ubuntu/comparapreco.github.io').resolve()
SITE = 'https://comparapreco.github.io'
SKIP_SCHEMES = {'mailto', 'tel', 'javascript', 'data'}

html_files = sorted([p for p in ROOT.rglob('*.html') if '.git' not in p.parts])
existing = set()
for p in html_files:
    rel = '/' + p.relative_to(ROOT).as_posix()
    existing.add(rel)
    if p.name == 'index.html':
        existing.add('/' + p.parent.relative_to(ROOT).as_posix().strip('/') + '/')
        if p.parent == ROOT:
            existing.add('/')
        else:
            existing.add('/' + p.parent.relative_to(ROOT).as_posix().strip('/'))

all_links = []
broken_internal = []
internal_counts = Counter()
external_counts = Counter()
anchor_only = 0
empty_href = []
text_issues = []
nav_links = defaultdict(set)

for p in html_files:
    rel_file = '/' + p.relative_to(ROOT).as_posix()
    try:
        soup = BeautifulSoup(p.read_text(encoding='utf-8', errors='ignore'), 'html.parser')
    except Exception as e:
        continue
    title = soup.title.get_text(' ', strip=True) if soup.title else ''
    main_text = soup.get_text(' ', strip=True)
    if any(x in main_text for x in ['seriam injetados aqui', 'Lorem ipsum', 'TODO', 'Em breve', 'Coming soon']):
        text_issues.append({'file': rel_file, 'title': title, 'issue': 'texto provisório ou placeholder detectado'})
    if 'Ninja PRO' in main_text and not (ROOT/'pro/index.html').exists() and not (ROOT/'pro.html').exists():
        text_issues.append({'file': rel_file, 'title': title, 'issue': 'menciona Ninja PRO, mas a página /pro não existe'})
    for a in soup.find_all('a'):
        href = (a.get('href') or '').strip()
        label = a.get_text(' ', strip=True)[:120]
        if not href:
            empty_href.append({'file': rel_file, 'label': label})
            continue
        href_no_frag, frag = urldefrag(href)
        if not href_no_frag and frag:
            anchor_only += 1
            continue
        parsed = urlparse(href_no_frag)
        if parsed.scheme in SKIP_SCHEMES:
            continue
        if parsed.scheme in ['http','https'] and parsed.netloc and parsed.netloc != 'comparapreco.github.io':
            external_counts[href_no_frag] += 1
            continue
        if parsed.netloc == 'comparapreco.github.io':
            path = parsed.path or '/'
        elif href_no_frag.startswith('/'):
            path = href_no_frag
        else:
            # relative path from current file directory
            base = '/' + p.parent.relative_to(ROOT).as_posix().strip('/')
            if base == '/.':
                base = '/'
            path = posixpath.normpath(posixpath.join(base, href_no_frag))
        path = unquote(path)
        if '?' in path:
            path = path.split('?',1)[0]
        # normalize slashes and relative segments
        path = posixpath.normpath(re.sub(r'/+', '/', path))
        if not path.startswith('/'):
            path = '/' + path
        if path != '/' and path.endswith('/'):
            candidates = [path, path[:-1], path + 'index.html']
        elif path.endswith('.html'):
            candidates = [path]
        else:
            candidates = [path, path + '/', path + '/index.html', path + '.html']
        ok = any(c in existing for c in candidates)
        internal_counts[path] += 1
        all_links.append({'file': rel_file, 'href': href, 'target': path, 'label': label, 'ok': ok})
        if not ok:
            broken_internal.append({'file': rel_file, 'href': href, 'target': path, 'label': label})
            nav_links[path].add(rel_file)

report = {
    'summary': {
        'html_files': len(html_files),
        'internal_unique_targets': len(internal_counts),
        'external_unique_targets': len(external_counts),
        'broken_internal_total_occurrences': len(broken_internal),
        'broken_internal_unique_targets': len(set(x['target'] for x in broken_internal)),
        'empty_href_total': len(empty_href),
        'anchor_only_total': anchor_only,
        'text_issue_total': len(text_issues),
    },
    'broken_internal_by_target': [
        {'target': t, 'occurrences': sum(1 for x in broken_internal if x['target']==t), 'sample_files': sorted(list(files))[:10]}
        for t, files in sorted(nav_links.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    ],
    'broken_internal_samples': broken_internal[:500],
    'text_issues': text_issues[:500],
    'top_internal_targets': internal_counts.most_common(50),
    'top_external_targets': external_counts.most_common(50),
}

out = ROOT/'AUDITORIA_LINKS_ATUAL.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report['summary'], ensure_ascii=False, indent=2))
print('\nPrincipais destinos internos quebrados:')
for item in report['broken_internal_by_target'][:40]:
    print(f"{item['target']}: {item['occurrences']} ocorrências")
print('\nProblemas de texto:')
for item in text_issues[:30]:
    print(f"{item['file']}: {item['issue']}")
