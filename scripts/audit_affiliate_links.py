#!/usr/bin/env python3
"""
AUDITORIA COMPLETA DE LINKS DE AFILIADO - COMPARA PREÇO
Verifica se cada produto HTML aponta para o MLB correto com o tag de afiliado.
"""

import os
import re
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs

BASE_DIR = Path(__file__).parent.parent
OFERTAS_DIR = BASE_DIR / "ofertas"
AFFILIATE_TAG = "vendas0nline"
AFFILIATE_PARAM = "matt_tool"

# Resultados da auditoria
results = {
    "corretos": [],
    "links_quebrados": [],
    "produto_divergente": [],
    "sem_tag_afiliado": [],
    "duplicados": [],
    "erros_parsing": []
}

# Mapa de IDs para detectar duplicatas
id_map = {}  # MLB_ID -> [lista de arquivos]

def extract_mlb_from_filename(filename):
    """Extrai o ID MLB do nome do arquivo HTML."""
    match = re.search(r'(MLB\d+)', filename)
    if match:
        return match.group(1)
    return None

def extract_mlb_from_url(url):
    """Extrai o ID MLB de uma URL do Mercado Livre."""
    if not url:
        return None
    # Padrão: /p/MLB12345 ou /MLB12345 ou MLB12345 no path
    match = re.search(r'/(MLB\d+)', url)
    if match:
        return match.group(1)
    # Padrão alternativo: MLB no query string
    match = re.search(r'(MLB\d+)', url)
    if match:
        return match.group(1)
    return None

def check_affiliate_tag(url):
    """Verifica se a URL contém o tag de afiliado correto."""
    if not url:
        return False
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    tag_value = params.get(AFFILIATE_PARAM, [None])[0]
    return tag_value == AFFILIATE_TAG

def audit_html_file(html_path):
    """Audita um arquivo HTML de produto."""
    filename = html_path.name
    mlb_from_file = extract_mlb_from_filename(filename)
    
    if not mlb_from_file:
        results["erros_parsing"].append({
            "arquivo": str(html_path.relative_to(BASE_DIR)),
            "erro": "Não foi possível extrair ID MLB do nome do arquivo"
        })
        return
    
    # Registrar para detecção de duplicatas
    if mlb_from_file not in id_map:
        id_map[mlb_from_file] = []
    id_map[mlb_from_file].append(str(html_path.relative_to(BASE_DIR)))
    
    # Ler o conteúdo do arquivo
    try:
        content = html_path.read_text(encoding='utf-8')
    except Exception as e:
        results["links_quebrados"].append({
            "arquivo": str(html_path.relative_to(BASE_DIR)),
            "mlb_arquivo": mlb_from_file,
            "erro": f"Erro ao ler arquivo: {e}"
        })
        return
    
    # Extrair o link principal de afiliado (botão "Ir para o Mercado Livre")
    # Padrão 1: botão principal
    btn_match = re.search(
        r'<a[^>]+class="btn"[^>]+href="(https://www\.mercadolivre[^"]+)"[^>]*>.*?Ir para o Mercado Livre',
        content, re.DOTALL
    )
    
    # Padrão 2: qualquer link ML com matt_tool
    if not btn_match:
        btn_match = re.search(
            r'href="(https://www\.mercadolivre[^"]*matt_tool[^"]*)"',
            content
        )
    
    # Padrão 3: link ML no schema.org
    if not btn_match:
        btn_match = re.search(
            r'"url":\s*"(https://www\.mercadolivre[^"]+)"',
            content
        )
    
    if not btn_match:
        results["links_quebrados"].append({
            "arquivo": str(html_path.relative_to(BASE_DIR)),
            "mlb_arquivo": mlb_from_file,
            "erro": "Nenhum link do Mercado Livre encontrado no arquivo"
        })
        return
    
    affiliate_url = btn_match.group(1)
    mlb_from_url = extract_mlb_from_url(affiliate_url)
    has_tag = check_affiliate_tag(affiliate_url)
    
    # Determinar o nome do produto (tag <title> ou <h1>)
    title_match = re.search(r'<title>([^<]+)</title>', content)
    product_name = title_match.group(1).strip() if title_match else filename
    
    # Classificar o resultado
    if not mlb_from_url:
        results["links_quebrados"].append({
            "arquivo": str(html_path.relative_to(BASE_DIR)),
            "produto": product_name,
            "mlb_arquivo": mlb_from_file,
            "url_afiliado": affiliate_url,
            "erro": "Não foi possível extrair ID MLB da URL de afiliado"
        })
    elif mlb_from_url != mlb_from_file:
        results["produto_divergente"].append({
            "arquivo": str(html_path.relative_to(BASE_DIR)),
            "produto": product_name,
            "mlb_arquivo": mlb_from_file,
            "mlb_url": mlb_from_url,
            "url_afiliado": affiliate_url,
            "tem_tag_afiliado": has_tag
        })
    elif not has_tag:
        results["sem_tag_afiliado"].append({
            "arquivo": str(html_path.relative_to(BASE_DIR)),
            "produto": product_name,
            "mlb_arquivo": mlb_from_file,
            "url_afiliado": affiliate_url
        })
    else:
        results["corretos"].append({
            "arquivo": str(html_path.relative_to(BASE_DIR)),
            "produto": product_name,
            "mlb": mlb_from_file,
            "url_afiliado": affiliate_url
        })

def audit_json_products():
    """Audita os arquivos JSON de produtos para verificar links de afiliado."""
    json_audit = []
    
    # Arquivos JSON principais a auditar
    json_files = [
        BASE_DIR / "data" / "database" / "all_products.json",
        BASE_DIR / "data" / "curated_products.json",
        BASE_DIR / "data" / "new_offers.json",
        BASE_DIR / "data" / "all_products_final_unique_urls.json",
    ]
    
    for json_path in json_files:
        if not json_path.exists():
            continue
        
        try:
            with open(json_path) as f:
                products = json.load(f)
        except Exception as e:
            json_audit.append({"arquivo": str(json_path.relative_to(BASE_DIR)), "erro": str(e)})
            continue
        
        if not isinstance(products, list):
            continue
        
        for p in products:
            pid = p.get('id', '')
            name = p.get('name', p.get('title', ''))
            permalink = p.get('permalink', '')
            affiliate_url = p.get('custom_affiliate_url', p.get('affiliate_url', ''))
            
            mlb_from_id = pid if pid.startswith('MLB') else None
            mlb_from_permalink = extract_mlb_from_url(permalink)
            mlb_from_affiliate = extract_mlb_from_url(affiliate_url)
            has_tag = check_affiliate_tag(affiliate_url)
            
            issues = []
            
            if not affiliate_url:
                issues.append("sem_url_afiliado")
            elif not has_tag:
                issues.append("sem_tag_afiliado")
            
            if mlb_from_id and mlb_from_affiliate and mlb_from_id != mlb_from_affiliate:
                issues.append(f"id_divergente: id={mlb_from_id} vs url={mlb_from_affiliate}")
            
            if mlb_from_permalink and mlb_from_affiliate and mlb_from_permalink != mlb_from_affiliate:
                # Pode ser normal se permalink usa /p/MLB diferente do item ID
                pass
            
            json_audit.append({
                "arquivo": str(json_path.relative_to(BASE_DIR)),
                "id": pid,
                "nome": name[:60],
                "permalink": permalink[:80] if permalink else "",
                "affiliate_url": affiliate_url[:80] if affiliate_url else "",
                "tem_tag": has_tag,
                "problemas": issues
            })
    
    return json_audit

# === EXECUTAR AUDITORIA ===
print("=" * 60)
print("AUDITORIA DE LINKS DE AFILIADO - COMPARA PREÇO")
print("=" * 60)
print(f"\nIdentificador de afiliado esperado: {AFFILIATE_TAG}")
print(f"Parâmetro: {AFFILIATE_PARAM}={AFFILIATE_TAG}\n")

# 1. Auditar todas as páginas HTML de produtos
html_files = list(OFERTAS_DIR.rglob("*.html"))
print(f"Total de páginas HTML encontradas: {len(html_files)}")

for html_path in sorted(html_files):
    audit_html_file(html_path)

# 2. Detectar duplicatas
for mlb_id, files in id_map.items():
    if len(files) > 1:
        results["duplicados"].append({
            "mlb_id": mlb_id,
            "arquivos": files,
            "total": len(files)
        })

# 3. Auditar JSONs
print("Auditando arquivos JSON de produtos...")
json_audit = audit_json_products()

# === SALVAR RELATÓRIO ===
report = {
    "resumo": {
        "total_html_auditados": len(html_files),
        "total_corretos": len(results["corretos"]),
        "total_sem_tag_afiliado": len(results["sem_tag_afiliado"]),
        "total_produto_divergente": len(results["produto_divergente"]),
        "total_links_quebrados": len(results["links_quebrados"]),
        "total_duplicados": len(results["duplicados"]),
        "total_erros_parsing": len(results["erros_parsing"]),
        "total_json_auditados": len(json_audit),
        "total_json_com_problemas": len([j for j in json_audit if j.get("problemas")])
    },
    "html_corretos": results["corretos"],
    "html_sem_tag_afiliado": results["sem_tag_afiliado"],
    "html_produto_divergente": results["produto_divergente"],
    "html_links_quebrados": results["links_quebrados"],
    "html_duplicados": results["duplicados"],
    "html_erros_parsing": results["erros_parsing"],
    "json_auditoria": json_audit
}

report_path = BASE_DIR / "data" / "affiliate_audit_report.json"
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

# === IMPRIMIR RESUMO ===
print("\n" + "=" * 60)
print("RESUMO DA AUDITORIA")
print("=" * 60)
s = report["resumo"]
print(f"  Total de páginas HTML auditadas : {s['total_html_auditados']}")
print(f"  ✅ Links corretos               : {s['total_corretos']}")
print(f"  ⚠️  Sem tag de afiliado          : {s['total_sem_tag_afiliado']}")
print(f"  ❌ Produto divergente (MLB ≠)   : {s['total_produto_divergente']}")
print(f"  🔴 Links quebrados/sem ML URL   : {s['total_links_quebrados']}")
print(f"  🔁 Produtos duplicados          : {s['total_duplicados']}")
print(f"  ⚙️  Erros de parsing             : {s['total_erros_parsing']}")
print(f"\n  JSONs auditados                 : {s['total_json_auditados']}")
print(f"  JSONs com problemas             : {s['total_json_com_problemas']}")

if results["produto_divergente"]:
    print("\n--- PRODUTOS DIVERGENTES (MLB no arquivo ≠ MLB na URL) ---")
    for p in results["produto_divergente"]:
        print(f"  ❌ {p['arquivo']}")
        print(f"     MLB arquivo: {p['mlb_arquivo']} | MLB URL: {p['mlb_url']}")
        print(f"     URL: {p['url_afiliado'][:80]}")

if results["sem_tag_afiliado"]:
    print("\n--- SEM TAG DE AFILIADO ---")
    for p in results["sem_tag_afiliado"]:
        print(f"  ⚠️  {p['arquivo']}")
        print(f"     URL: {p['url_afiliado'][:80]}")

if results["links_quebrados"]:
    print("\n--- LINKS QUEBRADOS ---")
    for p in results["links_quebrados"]:
        print(f"  🔴 {p['arquivo']}")
        print(f"     Erro: {p.get('erro', 'desconhecido')}")

if results["duplicados"]:
    print("\n--- PRODUTOS DUPLICADOS ---")
    for d in results["duplicados"]:
        print(f"  🔁 {d['mlb_id']} aparece {d['total']}x:")
        for f in d["arquivos"]:
            print(f"     - {f}")

print(f"\nRelatório salvo em: {report_path}")
print("=" * 60)
