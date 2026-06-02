import os
import json
import glob

def audit_orphans():
    db_path = "data/database/all_products.json"
    if not os.path.exists(db_path):
        print("Erro: Banco de dados não encontrado.")
        return

    with open(db_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    db_ids = {p['id'] for p in products}
    
    html_files = glob.glob("ofertas/**/*.html", recursive=True)
    
    orphans = []
    for file_path in html_files:
        # Extrair ID do nome do arquivo (formato: nome-produto-ID.html)
        filename = os.path.basename(file_path)
        try:
            p_id = filename.split('-')[-1].replace('.html', '')
            if p_id not in db_ids:
                orphans.append(file_path)
        except:
            orphans.append(file_path)

    print("="*50)
    print("AUDITORIA DE PÁGINAS ÓRFÃS / DUPLICADAS NO DISCO")
    print("="*50)
    print(f"Total de arquivos HTML em /ofertas: {len(html_files)}")
    print(f"Total de produtos no banco: {len(db_ids)}")
    print(f"Páginas órfãs (não estão no banco): {len(orphans)}")
    print("-" * 30)
    
    if orphans:
        print("Top 20 páginas órfãs:")
        for o in orphans[:20]:
            print(o)
            
    # Salvar lista para remoção
    with open("data/orphan_pages.json", "w", encoding="utf-8") as f:
        json.dump(orphans, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    audit_orphans()
