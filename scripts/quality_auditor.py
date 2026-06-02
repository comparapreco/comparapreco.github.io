import os
import json
from pathlib import Path
from bs4 import BeautifulSoup
from logger import logger

ROOT = Path(__file__).resolve().parents[1]

def audit_quality():
    logger.info("Iniciando Auditoria de Qualidade SEO...")
    issues = {
        "duplicate_titles": {},
        "thin_content": [],
        "missing_meta": [],
        "orphan_pages": []
    }
    
    titles = {}
    all_htmls = list(ROOT.rglob("*.html"))
    
    for html_file in all_htmls:
        if "admin/" in str(html_file) or "templates/" in str(html_file): continue
        
        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            
        # 1. Verificar Título
        title_tag = soup.find("title")
        if title_tag:
            t = title_tag.get_text().strip()
            if t in titles:
                if t not in issues["duplicate_titles"]: issues["duplicate_titles"][t] = []
                issues["duplicate_titles"][t].append(str(html_file.relative_to(ROOT)))
            titles[t] = str(html_file.relative_to(ROOT))
        
        # 2. Verificar Conteúdo Curto (Thin Content)
        text = soup.get_text()
        if len(text.split()) < 200: # Menos de 200 palavras
            issues["thin_content"].append(str(html_file.relative_to(ROOT)))
            
        # 3. Verificar Meta Description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if not meta_desc or not meta_desc.get("content"):
            issues["missing_meta"].append(str(html_file.relative_to(ROOT)))

    # Salvar relatório de qualidade
    with open(ROOT / "data" / "quality_audit.json", 'w') as f:
        json.dump(issues, f, indent=2)
    logger.info(f"Auditoria concluída. Problemas detectados: {len(issues['thin_content'])} páginas curtas, {len(issues['duplicate_titles'])} títulos duplicados.")

if __name__ == "__main__":
    audit_quality()
