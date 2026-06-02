import os
import json
from pathlib import Path
from bs4 import BeautifulSoup
from logger import logger

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://comparapreco.github.io"

def generate_breadcrumb_schema(items):
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": []
    }
    for i, (name, url) in enumerate(items, 1):
        schema["itemListElement"].append({
            "@type": "ListItem",
            "position": i,
            "name": name,
            "item": f"{BASE_URL}{url}" if url.startswith("/") else url
        })
    return f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'

def apply_to_file(file_path, breadcrumbs):
    if not file_path.exists(): return
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    soup = BeautifulSoup(content, "html.parser")
    
    # Criar HTML do Breadcrumb
    bc_html = '<nav class="breadcrumb-nav" style="margin: 20px 0; font-size: 14px; color: #666;">'
    bc_links = []
    for i, (name, url) in enumerate(breadcrumbs):
        if i == len(breadcrumbs) - 1:
            bc_links.append(f'<span style="font-weight: bold;">{name}</span>')
        else:
            bc_links.append(f'<a href="{url}" style="color: var(--primary); text-decoration: none;">{name}</a>')
    bc_html += " / ".join(bc_links) + "</nav>"
    
    # Injetar Schema no Head
    schema_tag = BeautifulSoup(generate_breadcrumb_schema(breadcrumbs), "html.parser")
    if soup.head:
        soup.head.append(schema_tag)
    
    # Injetar HTML no Main ou Body
    main = soup.find("main") or soup.body
    if main:
        # Inserir no topo do main
        main.insert(0, BeautifulSoup(bc_html, "html.parser"))
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

def main():
    logger.info("Aplicando Breadcrumbs em todo o portal...")
    
    # Exemplo: Aplicar em comparativos
    comp_dir = ROOT / "comparar"
    for f in comp_dir.glob("*.html"):
        name = f.name.replace(".html", "").replace("-", " ").title()
        apply_to_file(f, [("Home", "/"), ("Comparativos", "/comparar/"), (name, f"/comparar/{f.name}")])
        
    # Exemplo: Aplicar em rankings
    rank_dir = ROOT / "melhores-2026"
    for f in rank_dir.glob("*.html"):
        name = f.name.replace(".html", "").replace("-", " ").title()
        apply_to_file(f, [("Home", "/"), ("Melhores 2026", "/melhores-2026/"), (name, f"/melhores-2026/{f.name}")])

if __name__ == "__main__":
    main()
