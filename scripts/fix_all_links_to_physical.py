import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def get_physical_mapping():
    """Mapeia o ID do produto (MLB...) para o caminho real do arquivo no disco."""
    mapping = {}
    for path in ROOT.rglob("*-MLB*.html"):
        if "ofertas" in path.parts:
            # Extrair ID do nome do arquivo: slug-MLB123.html -> MLB123
            match = re.search(r'(MLB\d+)\.html$', path.name)
            if match:
                mlb_id = match.group(1)
                # Caminho relativo a partir da raiz do site
                rel_path = path.relative_to(ROOT).as_posix()
                mapping[mlb_id] = rel_path
    return mapping

def fix_links_in_file(file_path, mapping):
    try:
        content = file_path.read_text(encoding="utf-8")
        new_content = content
        
        # Encontrar links que contenham MLB...
        # Ex: href="./slug-MLB123.html" ou href="../../ofertas/cat/slug-MLB123.html"
        # Vamos focar em substituir o caminho inteiro baseado no ID
        
        # Regex para capturar o href que termina com um ID MLB e .html
        href_pattern = r'href="([^"]*?(MLB\d+)\.html)"'
        
        def replace_link(match):
            full_href = match.group(1)
            mlb_id = match.group(2)
            
            if mlb_id in mapping:
                actual_path = mapping[mlb_id]
                # Determinar profundidade do arquivo atual para ajustar o link relativo
                depth = len(file_path.relative_to(ROOT).parts) - 1
                prefix = "../" * depth if depth > 0 else "./"
                new_href = prefix + actual_path
                return f'href="{new_href}"'
            return match.group(0)

        new_content = re.sub(href_pattern, replace_link, new_content)
        
        if new_content != content:
            file_path.write_text(new_content, encoding="utf-8")
            return True
    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
    return False

def main():
    print("Iniciando correção de links baseada em arquivos físicos...")
    mapping = get_physical_mapping()
    print(f"Mapeados {len(mapping)} arquivos físicos de ofertas.")
    
    changed_count = 0
    html_files = list(ROOT.rglob("*.html"))
    
    for html_file in html_files:
        if fix_links_in_file(html_file, mapping):
            changed_count += 1
            
    print(f"Links corrigidos em {changed_count} arquivos.")

if __name__ == "__main__":
    main()
