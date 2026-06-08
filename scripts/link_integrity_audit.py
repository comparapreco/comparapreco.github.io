import os
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE_FILE = ROOT / "data/database/all_products.json"

def audit_links():
    if not DATABASE_FILE.exists():
        print("Erro: Banco de dados não encontrado.")
        return

    with open(DATABASE_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"Iniciando auditoria de integridade para {len(products)} produtos...")
    
    broken_links = []
    success_count = 0
    
    # Importar slugify do quality_utils para garantir paridade
    import sys
    sys.path.append(str(ROOT / "scripts"))
    from quality_utils import slugify, clean_product_name

    for p in products:
        p_id = str(p.get("id"))
        p_name = clean_product_name(p.get("name") or p.get("title"))
        p_slug = slugify(p_name)
        p_cat = p.get("custom_category_slug", "outros")
        
        # O formato esperado é ofertas/{categoria}/{slug}-{id}.html
        relative_path = f"ofertas/{p_cat}/{p_slug}-{p_id}.html"
        full_path = ROOT / relative_path
        
        if not full_path.exists():
            # Tentar encontrar o arquivo real para ver o que mudou
            real_files = list(ROOT.rglob(f"*{p_id}.html"))
            real_path = real_files[0].relative_to(ROOT).as_posix() if real_files else "NÃO ENCONTRADO"
            
            broken_links.append({
                "id": p_id,
                "expected": relative_path,
                "actual_on_disk": real_path,
                "name": p_name
            })
        else:
            success_count += 1

    print(f"Auditoria concluída: {success_count} links OK, {len(broken_links)} links QUEBRADOS.")
    
    if broken_links:
        report_path = ROOT / "data/broken_links_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(broken_links, f, indent=2, ensure_ascii=False)
        print(f"Relatório de links quebrados salvo em: {report_path}")
        
        # Mostrar os primeiros 5 para análise
        for bl in broken_links[:5]:
            print(f"\nID: {bl['id']}\nEsperado: {bl['expected']}\nNo disco: {bl['actual_on_disk']}")
    
    return broken_links

if __name__ == "__main__":
    audit_links()
