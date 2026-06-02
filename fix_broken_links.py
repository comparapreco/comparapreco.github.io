#!/usr/bin/env python3
"""
Script para corrigir links quebrados no site Compara Preço.
Estratégia:
1. Remover links para comparativos que não existem fisicamente
2. Remover links para páginas de produtos duplicadas
3. Manter apenas links para páginas que existem
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
        # Adicionar variações
        if html_file.name == 'index.html':
            dir_path = '/' + html_file.parent.relative_to(ROOT).as_posix().strip('/')
            if dir_path != '/':
                existing_files.add(dir_path + '/')
                existing_files.add(dir_path)

print(f"Total de arquivos HTML encontrados: {len(existing_files)}")

# Função para remover links quebrados de um arquivo
def fix_html_file(filepath):
    content = filepath.read_text(encoding='utf-8', errors='ignore')
    original_content = content
    
    # Padrão para links de comparativos "Outros Comparativos Populares"
    # Remover seções inteiras de comparativos quebrados
    pattern_section = r'<section class="related-links"[^>]*>.*?<h2>Outros Comparativos Populares</h2>.*?<ul>.*?</ul>.*?</section>'
    
    # Encontrar todos os links de comparativos
    link_pattern = r'<a href="(/comparar/[^"]*)"[^>]*>([^<]*)</a>'
    
    def replace_broken_links(match):
        href = match.group(1)
        text = match.group(2)
        # Verificar se o arquivo existe
        if href in existing_files or href + '.html' in existing_files:
            return match.group(0)  # Manter o link
        else:
            return ''  # Remover o link
    
    # Remover links quebrados dentro de listas
    content = re.sub(r'<li><a href="/comparar/[^"]*"[^>]*>[^<]*</a></li>', 
                     lambda m: m.group(0) if any(x in m.group(0) for x in existing_files) else '', 
                     content)
    
    # Se a seção de "Outros Comparativos" ficou vazia, remover a seção inteira
    content = re.sub(r'<section class="related-links"[^>]*>\s*<h2>Outros Comparativos Populares</h2>\s*<ul>\s*</ul>\s*</section>', '', content)
    
    if content != original_content:
        filepath.write_text(content, encoding='utf-8')
        return True
    return False

# Processar todos os arquivos HTML
fixed_count = 0
for html_file in ROOT.rglob('*.html'):
    if '.git' not in html_file.parts:
        if fix_html_file(html_file):
            fixed_count += 1
            print(f"Corrigido: {html_file.relative_to(ROOT)}")

print(f"\nTotal de arquivos corrigidos: {fixed_count}")
