import os
import re
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]

def find_links_in_html(content):
    """Extrai todos os links internos de um conteúdo HTML."""
    # Procura por href="../../ofertas/..." ou href="/ofertas/..."
    links = re.findall(r'href=["\'](.*?\.html)["\']', content)
    return links

def check_site_integrity():
    print("Iniciando Verificação de Integridade de Links...")
    
    html_files = list(ROOT.glob("**/*.html"))
    print(f"Encontrados {len(html_files)} arquivos HTML para auditar.")
    
    broken_links = []
    total_links_checked = 0
    
    for html_file in html_files:
        # Pular arquivos dentro de 'compara' se ainda existirem
        if "compara/" in str(html_file):
            continue
            
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        links = find_links_in_html(content)
        for link in links:
            if link.startswith(("http", "mailto", "tel", "#")):
                continue
                
            total_links_checked += 1
            
            # Resolver o caminho do link relativo ao arquivo atual
            if link.startswith("/"):
                target_path = ROOT / link.lstrip("/")
            else:
                target_path = (html_file.parent / link).resolve()
            
            if not target_path.exists():
                broken_links.append({
                    "source": str(html_file.relative_to(ROOT)),
                    "link": link,
                    "target_expected": str(target_path.relative_to(ROOT) if ROOT in target_path.parents else target_path)
                })

    print(f"Auditoria concluída. {total_links_checked} links verificados.")
    if broken_links:
        print(f"AVISO: Encontrados {len(broken_links)} links quebrados!")
        for bl in broken_links[:20]: # Mostrar os primeiros 20
            print(f"  Fonte: {bl['source']}")
            print(f"  Link: {bl['link']}")
            print(f"  Esperado: {bl['target_expected']}")
            print("-" * 20)
    else:
        print("SUCESSO: Nenhum link quebrado encontrado localmente.")
    
    return broken_links

if __name__ == "__main__":
    check_site_integrity()
