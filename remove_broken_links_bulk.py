#!/usr/bin/env python3
"""
Remove todos os links para comparativos que não existem fisicamente.
Estratégia: Remover qualquer <li> ou <a> que aponte para um arquivo inexistente.
"""
from pathlib import Path
import re

ROOT = Path('/home/ubuntu/comparapreco.github.io').resolve()

# Coletar todos os arquivos HTML que existem
existing_files = set()
for html_file in ROOT.rglob('*.html'):
    if '.git' not in html_file.parts:
        rel_path = '/' + html_file.relative_to(ROOT).as_posix()
        existing_files.add(rel_path)

print(f"Total de arquivos HTML encontrados: {len(existing_files)}")

# Função para remover links quebrados
def remove_broken_links(filepath):
    content = filepath.read_text(encoding='utf-8', errors='ignore')
    original_content = content
    
    # Remover <li> com links quebrados
    def check_link(match):
        href = match.group(1)
        # Normalizar o caminho
        if not href.endswith('.html') and not href.endswith('/'):
            href_html = href + '.html'
        else:
            href_html = href
        
        if href in existing_files or href_html in existing_files:
            return match.group(0)  # Manter
        else:
            return ''  # Remover
    
    # Remover <li><a href="...">...</a></li> com links quebrados
    content = re.sub(
        r'<li><a href="([^"]*)"[^>]*>[^<]*</a></li>',
        check_link,
        content
    )
    
    # Remover <section> vazio de "Outros Comparativos Populares"
    content = re.sub(
        r'<section class="related-links"[^>]*>\s*<h2>Outros Comparativos Populares</h2>\s*<ul>\s*</ul>\s*</section>',
        '',
        content
    )
    
    if content != original_content:
        filepath.write_text(content, encoding='utf-8')
        return True
    return False

# Processar todos os arquivos HTML
fixed_count = 0
for html_file in ROOT.rglob('*.html'):
    if '.git' not in html_file.parts:
        try:
            if remove_broken_links(html_file):
                fixed_count += 1
                rel_path = html_file.relative_to(ROOT)
                print(f"✓ Corrigido: {rel_path}")
        except Exception as e:
            print(f"✗ Erro em {html_file.relative_to(ROOT)}: {e}")

print(f"\nTotal de arquivos corrigidos: {fixed_count}")
