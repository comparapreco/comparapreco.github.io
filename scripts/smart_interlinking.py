import os
import json
import random
from pathlib import Path
from bs4 import BeautifulSoup
from logger import logger

ROOT = Path(__file__).resolve().parents[1]

def get_related_links(current_file, all_files, count=5):
    # Simples lógica de aleatoriedade para agora, pode ser melhorada com NLP/Categorias
    others = [f for f in all_files if f != current_file]
    return random.sample(others, min(len(others), count))

def apply_interlinking(file_path, related_files, title="Veja também"):
    if not file_path.exists(): return
    
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    section = soup.new_tag("section", attrs={"class": "related-links", "style": "margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px;"})
    h2 = soup.new_tag("h2")
    h2.string = title
    section.append(h2)
    
    ul = soup.new_tag("ul")
    for rf in related_files:
        li = soup.new_tag("li")
        a = soup.new_tag("a", href=f"/{rf.relative_to(ROOT)}")
        a.string = rf.name.replace(".html", "").replace("-", " ").title()
        li.append(a)
        ul.append(li)
    
    section.append(ul)
    
    main = soup.find("main") or soup.body
    if main:
        main.append(section)
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

def main():
    logger.info("Iniciando interligação inteligente...")
    
    # Interligar comparativos entre si
    comp_dir = ROOT / "comparar"
    all_comps = list(comp_dir.glob("*.html"))
    for f in all_comps:
        related = get_related_links(f, all_comps)
        apply_interlinking(f, related, "Outros Comparativos Populares")
        
    # Interligar rankings com comparativos
    rank_dir = ROOT / "melhores-2026"
    all_ranks = list(rank_dir.glob("*.html"))
    for f in all_ranks:
        related = get_related_links(f, all_comps, count=10)
        apply_interlinking(f, related, "Comparativos Relacionados a este Ranking")

if __name__ == "__main__":
    main()
