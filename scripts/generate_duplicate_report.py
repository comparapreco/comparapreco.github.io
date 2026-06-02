import json
import os
from collections import defaultdict
from difflib import SequenceMatcher
from logger import logger
import unicodedata
import re
from datetime import datetime

DB_PATH = "data/database/all_products.json"
REPORT_PATH = "reports/duplicate_report.md"
SIMILARITY_THRESHOLD = 0.9 # Limiar para similaridade de nomes

def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text

def generate_duplicate_report():
    logger.info("Gerando relatório de duplicados...")
    
    if not os.path.exists(DB_PATH):
        logger.warning(f"Banco de dados não encontrado em {DB_PATH}. Não é possível gerar relatório.")
        return

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            products = json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler banco de dados para relatório: {e}")
        return

    total_products = len(products)
    active_products = sum(1 for p in products if p.get("status") == "active")

    # Dicionários para encontrar duplicados
    sku_map = defaultdict(list)
    permalink_map = defaultdict(list)
    name_slug_map = defaultdict(list)

    for p in products:
        if p.get("sku"): sku_map[p["sku"]].append(p)
        if p.get("permalink"): permalink_map[p["permalink"]].append(p)
        if p.get("name"): name_slug_map[slugify(p["name"])].append(p)

    duplicate_skus = {sku: prods for sku, prods in sku_map.items() if len(prods) > 1}
    duplicate_permalinks = {pl: prods for pl, prods in permalink_map.items() if len(prods) > 1}
    duplicate_names = {}

    # Busca por similaridade de nomes (mais custosa)
    processed_names = set()
    for i, p1 in enumerate(products):
        name1_slug = slugify(p1.get("name", ""))
        if not name1_slug or name1_slug in processed_names: continue

        similar_group = [p1]
        for j, p2 in enumerate(products):
            if i >= j: continue # Evitar comparações redundantes
            name2_slug = slugify(p2.get("name", ""))
            if not name2_slug or name2_slug in processed_names: continue

            if SequenceMatcher(None, name1_slug, name2_slug).ratio() >= SIMILARITY_THRESHOLD:
                similar_group.append(p2)
                processed_names.add(name2_slug)
        
        if len(similar_group) > 1:
            duplicate_names[name1_slug] = similar_group
        processed_names.add(name1_slug)

    total_duplicates_found = len(duplicate_skus) + len(duplicate_permalinks) + len(duplicate_names)

    report_content = f"""# 📊 Relatório de Duplicação do Radar Ninja - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Este relatório detalha a saúde do banco de dados de produtos, identificando e categorizando possíveis duplicados.

## Resumo Geral

| Métrica | Valor |
|---|---|
| Total de Produtos no Banco | {total_products} |
| Produtos Ativos | {active_products} |
| Duplicados Encontrados (SKU/Permalink/Nome Similar) | {total_duplicates_found} |
| Taxa de Duplicação (aprox.) | {total_duplicates_found / total_products * 100 if total_products > 0 else 0:.2f}% |

## Detalhes dos Duplicados

### Duplicados por SKU

"""
    if not duplicate_skus:
        report_content += "Nenhum duplicado por SKU encontrado.\n"
    else:
        for sku, prods in duplicate_skus.items():
            report_content += f"\n#### SKU: `{sku}`\n"
            report_content += "| ID | Nome do Produto | Permalink | Status |\n"
            report_content += "|---|---|---|---|\n"
            for p in prods:
                report_content += f"| {p.get('id', 'N/A')} | {p.get('name', 'N/A')} | {p.get('permalink', 'N/A')} | {p.get('status', 'N/A')} |\n"

    report_content += f"""

### Duplicados por Permalink

"""
    if not duplicate_permalinks:
        report_content += "Nenhum duplicado por Permalink encontrado.\n"
    else:
        for pl, prods in duplicate_permalinks.items():
            report_content += f"\n#### Permalink: `{pl}`\n"
            report_content += "| ID | Nome do Produto | SKU | Status |\n"
            report_content += "|---|---|---|---|\n"
            for p in prods:
                report_content += f"| {p.get('id', 'N/A')} | {p.get('name', 'N/A')} | {p.get('sku', 'N/A')} | {p.get('status', 'N/A')} |\n"

    report_content += f"""

### Duplicados por Nome Similar (Acima de {SIMILARITY_THRESHOLD*100:.0f}% de similaridade)

"""
    if not duplicate_names:
        report_content += "Nenhum duplicado por nome similar encontrado.\n"
    else:
        for name_slug, prods in duplicate_names.items():
            report_content += f"\n#### Nome Slug: `{name_slug}`\n"
            report_content += "| ID | Nome do Produto | SKU | Permalink | Status |\n"
            report_content += "|---|---|---|---|---|\n"
            for p in prods:
                report_content += f"| {p.get('id', 'N/A')} | {p.get('name', 'N/A')} | {p.get('sku', 'N/A')} | {p.get('permalink', 'N/A')} | {p.get('status', 'N/A')} |\n"

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
    logger.info(f"Relatório de duplicados gerado em {REPORT_PATH}")

if __name__ == "__main__":
    generate_duplicate_report()
