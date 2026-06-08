import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE_FILE = ROOT / "data/database/all_products.json"

def fix_encoding(text):
    if not isinstance(text, str):
        return text
    # Mapa de correções comuns de codificação corrompida (latin1 -> utf8)
    replacements = {
        "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
        "Ã£": "ã", "Ãµ": "õ", "Ã¢": "â", "Ãª": "ê", "Ã´": "ô",
        "Ã§": "ç", "Ã ": "à", "Ã": "Á", "Ã‰": "É", "Ã": "Í",
        "Ã“": "Ó", "Ãš": "Ú", "Ãƒ": "Ã", "Ã•": "Õ", "Ã‚": "Â",
        "ÃŠ": "Ê", "Ã”": "Ô", "Ã‡": "Ç", "Ã€": "À",
        "Â ": " ", "Ã": "í", "Ã": "Á", "Ã³": "ó"
    }
    # Caso específico de "Ãrabe" que aparece nos logs
    text = text.replace("Ãrabe", "Árabe").replace("Ã¡rabe", "árabe")
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def fix_database():
    if not DATABASE_FILE.exists():
        print("Banco de dados não encontrado.")
        return
    
    with open(DATABASE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    changed = 0
    for p in data:
        old_name = p.get("name", "")
        p["name"] = fix_encoding(old_name)
        p["title"] = fix_encoding(p.get("title", ""))
        if p["name"] != old_name:
            changed += 1
            
    if changed > 0:
        with open(DATABASE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Banco de dados corrigido: {changed} produtos atualizados.")
    else:
        print("Nenhuma inconsistência encontrada no banco de dados.")

def fix_html_files():
    changed_files = 0
    # Alvos: ofertas, noticias, categorias e a raiz
    targets = [ROOT / "ofertas", ROOT / "noticias", ROOT / "categorias", ROOT / "index.html"]
    
    files = []
    for t in targets:
        if t.is_file():
            files.append(t)
        elif t.exists():
            files.extend(t.rglob("*.html"))
            
    for path in files:
        try:
            content = path.read_text(encoding="utf-8")
            new_content = fix_encoding(content)
            
            # Corrigir também escapes de barra unicode que podem quebrar links
            new_content = new_content.replace("\\u002F", "/").replace("\\u002f", "/")
            
            if new_content != content:
                path.write_text(new_content, encoding="utf-8")
                changed_files += 1
        except Exception as e:
            print(f"Erro ao processar {path}: {e}")
            
    print(f"Arquivos HTML corrigidos: {changed_files}")

if __name__ == "__main__":
    print("Iniciando reparo de emergência de codificação...")
    fix_database()
    fix_html_files()
    print("Reparo concluído.")
