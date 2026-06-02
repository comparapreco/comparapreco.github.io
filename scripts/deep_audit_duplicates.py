import json
import os
import unicodedata
from collections import Counter

def slugify(text: str) -> str:
    if not text: return ""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.lower().replace(' ', '-')
    return ''.join(c for c in text if c.isalnum() or c == '-')

def clean_url(url):
    if not url: return ""
    return url.split('?')[0].split('#')[0].rstrip('/')

def run_audit(db_path):
    if not os.path.exists(db_path):
        print(f"Erro: Arquivo {db_path} não encontrado.")
        return

    with open(db_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    total_products = len(products)
    ids = [p.get('id') for p in products if p.get('id')]
    urls = [clean_url(p.get('permalink') or p.get('url') or p.get('custom_affiliate_url')) for p in products]
    names = [slugify(p.get('name') or p.get('title')) for p in products]

    id_counts = Counter(ids)
    url_counts = Counter(urls)
    name_counts = Counter(names)

    duplicate_ids = {k: v for k, v in id_counts.items() if v > 1}
    duplicate_urls = {k: v for k, v in url_counts.items() if v > 1 and k}
    duplicate_names = {k: v for k, v in name_counts.items() if v > 1 and k}

    print("="*50)
    print("RELATÓRIO DE AUDITORIA DE DUPLICADOS - RADAR NINJA")
    print("="*50)
    print(f"Produtos totais: {total_products}")
    print(f"IDs duplicados: {len(duplicate_ids)}")
    print(f"URLs duplicadas: {len(duplicate_urls)}")
    print(f"Nomes (slugs) duplicados: {len(duplicate_names)}")
    print("-" * 30)
    
    unique_ids = len(set(ids))
    unique_urls = len(set(urls))
    unique_names = len(set(names))
    
    print(f"Produtos únicos (por ID): {unique_ids}")
    print(f"Produtos únicos (por URL): {unique_urls}")
    print(f"Produtos únicos (por Nome): {unique_names}")
    
    print("-" * 30)
    print("Top 10 IDs mais duplicados:")
    for k, v in sorted(duplicate_ids.items(), key=lambda item: item[1], reverse=True)[:10]:
        print(f"ID: {k} - Ocorrências: {v}")
        
    print("-" * 30)
    print("Top 10 Nomes mais duplicados:")
    for k, v in sorted(duplicate_names.items(), key=lambda item: item[1], reverse=True)[:10]:
        print(f"Slug: {k} - Ocorrências: {v}")

    # Salvar relatório detalhado
    report = {
        "total": total_products,
        "unique_ids": unique_ids,
        "duplicate_ids": duplicate_ids,
        "duplicate_urls": duplicate_urls,
        "duplicate_names": duplicate_names
    }
    
    with open("data/audit_duplicates_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_audit("data/database/all_products.json")
