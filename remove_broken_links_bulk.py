#!/usr/bin/env python3
"""
Script para remover todos os links <a> que apontam para arquivos HTML internos inexistentes.
"""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urldefrag, unquote
import re
import posixpath

ROOT = Path("/home/ubuntu/comparapreco.github.io").resolve()

# Coletar todos os arquivos HTML que existem no sistema de arquivos
existing_files = set()
for html_file in ROOT.rglob("*.html"):
    if ".git" not in html_file.parts:
        rel_path = "/" + html_file.relative_to(ROOT).as_posix()
        existing_files.add(rel_path)
        # Adicionar variações para index.html (ex: /pasta/index.html -> /pasta/)
        if html_file.name == "index.html":
            dir_path = "/" + html_file.parent.relative_to(ROOT).as_posix().strip("/")
            if dir_path != "/":
                existing_files.add(dir_path + "/")
                existing_files.add(dir_path)
            else:
                existing_files.add("/")

print(f"Total de arquivos HTML existentes mapeados: {len(existing_files)}")

def normalize_path(href, current_file_path):
    # Resolve paths like ../../file.html
    if href.startswith("/"):
        path = href
    else:
        # For relative hrefs, join with the current file's directory
        current_dir_posix = "/" + current_file_path.parent.relative_to(ROOT).as_posix().strip("/")
        if current_dir_posix == "/.": # Handle root directory case
            current_dir_posix = "/"
        path = posixpath.normpath(posixpath.join(current_dir_posix, href))

    path = unquote(path)
    if "?" in path:
        path = path.split("?", 1)[0]
    # Ensure path starts with /
    if not path.startswith("/"):
        path = "/" + path
    return path

def remove_broken_links_from_file(filepath):
    content = filepath.read_text(encoding="utf-8", errors="ignore")
    original_content = content
    soup = BeautifulSoup(content, "html.parser")
    
    current_rel_path = filepath.relative_to(ROOT)

    for a_tag in soup.find_all("a"):
        href = a_tag.get("href")
        if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:") or href.startswith("data:") or href.startswith("http"):
            continue # Ignorar âncoras, emails, telefones, scripts e links externos

        # Ignorar links com placeholders de template
        if "{{" in href and "}}" in href:
            continue

        normalized_href = normalize_path(href, filepath)
        
        # Verificar se o link aponta para um arquivo HTML interno que não existe
        # e não é um link de template
        if not (normalized_href in existing_files or (normalized_href + ".html") in existing_files):
            # Remover o link. Se for um <li><a>, remove o <li> inteiro.
            parent_li = a_tag.find_parent("li")
            if parent_li:
                parent_li.decompose()
            else:
                a_tag.decompose() # Remove apenas o <a>

    # Remover seções de "Outros Comparativos Populares" que ficaram vazias
    for section in soup.find_all("section", class_="related-links"):
        h2_tag = section.find("h2", string="Outros Comparativos Populares")
        if h2_tag:
            ul_tag = section.find("ul")
            if ul_tag and not ul_tag.find("li"):
                section.decompose()

    new_content = str(soup)
    if new_content != original_content:
        filepath.write_text(new_content, encoding="utf-8")
        return True
    return False

# Processar todos os arquivos HTML
fixed_count = 0
for html_file in ROOT.rglob("*.html"):
    if ".git" not in html_file.parts and "templates" not in html_file.parts:
        try:
            if remove_broken_links_from_file(html_file):
                fixed_count += 1
                rel_path = html_file.relative_to(ROOT)
                print(f"✓ Corrigido: {rel_path}")
        except Exception as e:
            print(f"✗ Erro em {html_file.relative_to(ROOT)}: {e}")

print(f"\nTotal de arquivos corrigidos: {fixed_count}")
