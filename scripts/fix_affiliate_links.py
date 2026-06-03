#!/usr/bin/env python3
"""
CORREÇÃO AUTOMÁTICA DE LINKS DE AFILIADO - COMPARA PREÇO
Corrige:
1. Links sem tag de afiliado (adiciona matt_tool=vendas0nline)
2. Produtos com ID duplicado mas nomes completamente diferentes (remove o errado)
3. Produtos duplicados em categorias diferentes (mantém o mais relevante, remove o outro)
4. Atualiza o all_products.json removendo produtos com IDs reutilizados incorretamente
"""

import os
import re
import json
import shutil
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

BASE_DIR = Path(__file__).parent.parent
OFERTAS_DIR = BASE_DIR / "ofertas"
AFFILIATE_TAG = "vendas0nline"
AFFILIATE_PARAM = "matt_tool"

# Registro de correções
corrections_log = {
    "tag_afiliado_adicionada": [],
    "duplicados_removidos": [],
    "produtos_removidos_json": [],
    "erros": []
}

def add_affiliate_tag(url):
    """Adiciona o tag de afiliado a uma URL do Mercado Livre."""
    if not url:
        return url
    if f"{AFFILIATE_PARAM}={AFFILIATE_TAG}" in url:
        return url  # Já tem o tag correto
    
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params[AFFILIATE_PARAM] = [AFFILIATE_TAG]
    
    new_query = urlencode(params, doseq=True)
    new_url = urlunparse((
        parsed.scheme, parsed.netloc, parsed.path,
        parsed.params, new_query, parsed.fragment
    ))
    return new_url

def fix_html_affiliate_tag(html_path):
    """Adiciona tag de afiliado a todos os links ML em um arquivo HTML."""
    try:
        content = html_path.read_text(encoding='utf-8')
        original = content
        
        # Substituir todos os links ML sem tag de afiliado
        def replace_ml_url(match):
            url = match.group(1)
            if 'mercadolivre.com' in url and AFFILIATE_PARAM not in url:
                new_url = add_affiliate_tag(url)
                return match.group(0).replace(url, new_url)
            return match.group(0)
        
        # Padrão para href="..."
        content = re.sub(r'href="(https://www\.mercadolivre[^"]+)"', replace_ml_url, content)
        # Padrão para "url": "..."
        content = re.sub(r'"url":\s*"(https://www\.mercadolivre[^"]+)"', 
                        lambda m: m.group(0).replace(m.group(1), add_affiliate_tag(m.group(1))), 
                        content)
        
        if content != original:
            html_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        corrections_log["erros"].append(f"Erro ao corrigir {html_path}: {e}")
        return False

def remove_html_file(html_path, reason):
    """Remove um arquivo HTML e registra a remoção."""
    try:
        if html_path.exists():
            html_path.unlink()
            corrections_log["duplicados_removidos"].append({
                "arquivo": str(html_path.relative_to(BASE_DIR)),
                "motivo": reason
            })
            return True
    except Exception as e:
        corrections_log["erros"].append(f"Erro ao remover {html_path}: {e}")
    return False

# ============================================================
# PASSO 1: Corrigir links sem tag de afiliado
# ============================================================
print("=" * 60)
print("PASSO 1: Corrigindo links sem tag de afiliado")
print("=" * 60)

with open(BASE_DIR / "data" / "affiliate_audit_report.json") as f:
    audit = json.load(f)

sem_tag = audit["html_sem_tag_afiliado"]
print(f"Produtos sem tag de afiliado: {len(sem_tag)}")

for item in sem_tag:
    html_path = BASE_DIR / item["arquivo"]
    if fix_html_affiliate_tag(html_path):
        corrections_log["tag_afiliado_adicionada"].append({
            "arquivo": item["arquivo"],
            "produto": item.get("produto", ""),
            "url_original": item["url_afiliado"],
            "url_corrigida": add_affiliate_tag(item["url_afiliado"])
        })
        print(f"  ✅ Tag adicionada: {item['arquivo']}")
    else:
        print(f"  ⚠️  Sem alteração: {item['arquivo']}")

# ============================================================
# PASSO 2: Remover produtos com ID duplicado e nomes diferentes
# ============================================================
print("\n" + "=" * 60)
print("PASSO 2: Removendo produtos com IDs duplicados e nomes diferentes")
print("=" * 60)

# IDs críticos: mesmo MLB ID, produtos completamente diferentes
# Estratégia: manter o arquivo na categoria mais correta, remover o outro
# Regra: se um arquivo está em 'outros' e o outro em categoria específica, remover o de 'outros'
# Se ambos em 'outros', manter o que tem mais palavras no nome (mais específico)

critical_dups = {
    "MLB25708528": {
        "manter": "ofertas/beleza/perfume-asad-elixir-lattafa-arabe-original-nota-fiscal-MLB25708528.html",
        "remover": "ofertas/outros/papel-higienico-familiar-folha-dupla-24-rolos-MLB25708528.html",
        "motivo": "ID MLB25708528 pertence ao perfume (categoria beleza), não ao papel higiênico"
    },
    "MLB66453791": {
        "manter": "ofertas/beleza/perfume-masculino-arabe-salvo-eua-de-parfum-alhmabra-100ml-original-cu002f-nf-MLB66453791.html",
        "remover": "ofertas/outros/secador-de-cabelos-philco-psc3500-4-em-1-dobravel-motor-bldc-prateado-bege-220v-MLB66453791.html",
        "motivo": "ID MLB66453791 pertence ao perfume (categoria beleza), não ao secador"
    },
    "MLB49089309": {
        "manter": "ofertas/celulares/celular-samsung-galaxy-a07-256gb-8gb-camera-50mp-tela-67--protecao-ip54-processador-6nm---preto-MLB49089309.html",
        "remover": "ofertas/informatica/notebook-asus-vivobook-15-m1502-amd-ryzen-7-8-gb-ram-512-gb-ssd-MLB49089309.html",
        "motivo": "ID MLB49089309 pertence ao Samsung Galaxy A07, não ao notebook Asus"
    },
    "MLB46220740": {
        "manter": "ofertas/celulares/samsung-galaxy-a06-5g-dual-sim-128gb-preto-MLB46220740.html",
        "remover": "ofertas/outros/jogo-toalhas-banho-grossas-macias-algodao-4pc-absorventes-MLB46220740.html",
        "motivo": "ID MLB46220740 pertence ao Samsung Galaxy A06 5G, não ao jogo de toalhas"
    },
    "MLB42835779": {
        "manter": "ofertas/eletrodomesticos/fritadeira-eletrica-afon-12l-bg-forno-oven-12-litros-preto-mondial-127v-MLB42835779.html",
        "remover": "ofertas/outros/jogo-de-jantar-e-cha-oxford-mendi-marfim-de-ceramica-com-20-pecas-bege-marfim-MLB42835779.html",
        "motivo": "ID MLB42835779 pertence à fritadeira Mondial, não ao jogo de jantar"
    },
    "MLB65664882": {
        "manter": "ofertas/informatica/computador-completo-top-intel-core-i5-4570-8gb-ram-ssd-256gb-bivolt-monitor-20--led-75hz-preto---bluepc-cd2e-0110to-256-gb-8-gb-MLB65664882.html",
        "remover": "ofertas/outros/testo-essencial---formula-exclusiva-com-feno-grego--boro--arginina--zma---precursor-da-testosterona---60-capsulas-sem-sabor-MLB65664882.html",
        "motivo": "ID MLB65664882 pertence ao computador BluePc, não ao suplemento Testo"
    },
    "MLB19479467": {
        "manter": "ofertas/outros/ar-condicionado-hw-lg-dual-inverter-voice-ai-9000-fr-branco-220v-MLB19479467.html",
        "remover": "ofertas/outros/jogo-toalhas-banho-grossas-macias-algodao-4pc-absorventes-MLB19479467.html",
        "motivo": "ID MLB19479467 pertence ao ar-condicionado LG, não ao jogo de toalhas"
    }
}

for mlb_id, action in critical_dups.items():
    remover_path = BASE_DIR / action["remover"]
    print(f"\n  🔴 MLB ID: {mlb_id}")
    print(f"     Mantendo: {action['manter']}")
    print(f"     Removendo: {action['remover']}")
    print(f"     Motivo: {action['motivo']}")
    
    if remove_html_file(remover_path, action["motivo"]):
        print(f"     ✅ Removido com sucesso")
    else:
        print(f"     ⚠️  Arquivo não encontrado ou erro")

# ============================================================
# PASSO 3: Tratar duplicatas de mesmo produto em categorias diferentes
# ============================================================
print("\n" + "=" * 60)
print("PASSO 3: Removendo duplicatas de mesmo produto em categorias diferentes")
print("=" * 60)

# Para duplicatas do mesmo produto em categorias diferentes,
# manter o da categoria mais específica, remover o de 'outros'
same_product_dups = []
for d in audit["html_duplicados"]:
    mlb_id = d["mlb_id"]
    if mlb_id in critical_dups:
        continue  # Já tratado acima
    
    files = d["arquivos"]
    # Verificar se algum está em 'outros'
    outros_files = [f for f in files if '/outros/' in f]
    specific_files = [f for f in files if '/outros/' not in f]
    
    if outros_files and specific_files:
        # Remover os de 'outros', manter os de categoria específica
        for f in outros_files:
            same_product_dups.append({
                "mlb_id": mlb_id,
                "remover": f,
                "manter": specific_files[0],
                "motivo": f"Mesmo produto ({mlb_id}) em categoria específica e em 'outros' - removendo de 'outros'"
            })
    elif len(outros_files) > 1:
        # Ambos em 'outros' - manter o primeiro, remover os demais
        for f in outros_files[1:]:
            same_product_dups.append({
                "mlb_id": mlb_id,
                "remover": f,
                "manter": outros_files[0],
                "motivo": f"Produto duplicado ({mlb_id}) em 'outros' - mantendo apenas uma cópia"
            })
    elif len(specific_files) > 1:
        # Ambos em categorias específicas - manter o primeiro
        for f in specific_files[1:]:
            same_product_dups.append({
                "mlb_id": mlb_id,
                "remover": f,
                "manter": specific_files[0],
                "motivo": f"Produto duplicado ({mlb_id}) em múltiplas categorias - mantendo apenas uma cópia"
            })

print(f"Duplicatas de mesmo produto a remover: {len(same_product_dups)}")
for dup in same_product_dups:
    remover_path = BASE_DIR / dup["remover"]
    print(f"\n  🔁 MLB ID: {dup['mlb_id']}")
    print(f"     Mantendo: {dup['manter']}")
    print(f"     Removendo: {dup['remover']}")
    
    if remove_html_file(remover_path, dup["motivo"]):
        print(f"     ✅ Removido com sucesso")
    else:
        print(f"     ⚠️  Arquivo não encontrado ou erro")

# ============================================================
# PASSO 4: Limpar produtos inválidos do all_products.json
# ============================================================
print("\n" + "=" * 60)
print("PASSO 4: Limpando produtos inválidos do banco de dados JSON")
print("=" * 60)

# IDs que foram identificados como pertencendo a produtos errados
# (os arquivos HTML foram removidos, agora remover do JSON também)
ids_to_remove_from_json = set()

# Produtos removidos por serem duplicatas com IDs errados
wrong_products = {
    # MLB ID -> nome do produto que NÃO deve estar associado a esse ID
    "MLB25708528": "papel-higienico",
    "MLB66453791": "secador-de-cabelos-philco",
    "MLB49089309": "notebook-asus-vivobook",
    "MLB46220740": "jogo-toalhas",
    "MLB42835779": "jogo-de-jantar",
    "MLB65664882": "testo-essencial",
    "MLB19479467": "jogo-toalhas",
}

# Verificar e limpar os JSONs principais
json_files_to_clean = [
    BASE_DIR / "data" / "database" / "all_products.json",
    BASE_DIR / "data" / "curated_products.json",
    BASE_DIR / "data" / "new_offers.json",
    BASE_DIR / "data" / "all_products_final_unique_urls.json",
]

for json_path in json_files_to_clean:
    if not json_path.exists():
        continue
    
    try:
        with open(json_path) as f:
            products = json.load(f)
        
        original_count = len(products)
        cleaned = []
        removed = []
        
        for p in products:
            pid = p.get('id', '')
            name = p.get('name', p.get('title', '')).lower()
            
            # Verificar se este produto tem um ID que foi reutilizado incorretamente
            should_remove = False
            if pid in wrong_products:
                wrong_keyword = wrong_products[pid]
                if wrong_keyword in name.replace(' ', '-'):
                    should_remove = True
                    removed.append({'id': pid, 'name': name[:60]})
            
            if not should_remove:
                cleaned.append(p)
        
        if len(cleaned) < original_count:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(cleaned, f, ensure_ascii=False, indent=2)
            
            print(f"\n  ✅ {json_path.name}: {original_count} -> {len(cleaned)} produtos")
            for r in removed:
                print(f"     Removido: {r['id']} - {r['name']}")
                corrections_log["produtos_removidos_json"].append({
                    "arquivo_json": str(json_path.relative_to(BASE_DIR)),
                    "id": r['id'],
                    "nome": r['name']
                })
        else:
            print(f"  ✓ {json_path.name}: sem alterações necessárias ({original_count} produtos)")
    
    except Exception as e:
        corrections_log["erros"].append(f"Erro ao limpar {json_path}: {e}")
        print(f"  ❌ Erro em {json_path.name}: {e}")

# ============================================================
# PASSO 5: Verificar e corrigir o data/products/offers.json
# ============================================================
print("\n" + "=" * 60)
print("PASSO 5: Verificando data/products/offers.json")
print("=" * 60)

offers_path = BASE_DIR / "data" / "products" / "offers.json"
if offers_path.exists():
    with open(offers_path) as f:
        offers = json.load(f)
    
    # Verificar se há produtos de teste
    test_products = [p for p in offers if p.get('id', '').startswith('TESTE_')]
    real_products = [p for p in offers if not p.get('id', '').startswith('TESTE_')]
    
    print(f"  Total de ofertas: {len(offers)}")
    print(f"  Produtos de teste: {len(test_products)}")
    print(f"  Produtos reais: {len(real_products)}")
    
    if test_products:
        print(f"  ⚠️  Removendo {len(test_products)} produtos de teste do offers.json")
        with open(offers_path, 'w', encoding='utf-8') as f:
            json.dump(real_products, f, ensure_ascii=False, indent=2)
        corrections_log["produtos_removidos_json"].append({
            "arquivo_json": "data/products/offers.json",
            "motivo": f"Removidos {len(test_products)} produtos de teste (ID TESTE_*)",
            "ids_removidos": [p['id'] for p in test_products]
        })
        print(f"  ✅ Removidos {len(test_products)} produtos de teste")
    else:
        print(f"  ✓ Sem produtos de teste")
    
    # Verificar se todos os links têm tag de afiliado
    missing_tag = [p for p in real_products if 
                   p.get('permalink') and 
                   'mercadolivre' in p.get('permalink', '') and 
                   AFFILIATE_PARAM not in p.get('permalink', '')]
    
    if missing_tag:
        print(f"  ⚠️  {len(missing_tag)} produtos sem tag de afiliado no permalink")
        # Corrigir
        for p in real_products:
            if p.get('permalink') and 'mercadolivre' in p.get('permalink', ''):
                if AFFILIATE_PARAM not in p.get('permalink', ''):
                    p['permalink'] = add_affiliate_tag(p['permalink'])
        
        with open(offers_path, 'w', encoding='utf-8') as f:
            json.dump(real_products, f, ensure_ascii=False, indent=2)
        print(f"  ✅ Tags de afiliado adicionadas ao offers.json")

# ============================================================
# SALVAR LOG DE CORREÇÕES
# ============================================================
print("\n" + "=" * 60)
print("SALVANDO LOG DE CORREÇÕES")
print("=" * 60)

corrections_log["resumo"] = {
    "tags_afiliado_adicionadas": len(corrections_log["tag_afiliado_adicionada"]),
    "duplicados_removidos": len(corrections_log["duplicados_removidos"]),
    "produtos_removidos_json": len(corrections_log["produtos_removidos_json"]),
    "erros": len(corrections_log["erros"])
}

log_path = BASE_DIR / "data" / "affiliate_corrections_log.json"
with open(log_path, 'w', encoding='utf-8') as f:
    json.dump(corrections_log, f, ensure_ascii=False, indent=2)

print(f"\nResumo das correções:")
print(f"  ✅ Tags de afiliado adicionadas : {corrections_log['resumo']['tags_afiliado_adicionadas']}")
print(f"  🗑️  Arquivos HTML removidos      : {corrections_log['resumo']['duplicados_removidos']}")
print(f"  🗑️  Produtos removidos de JSONs  : {corrections_log['resumo']['produtos_removidos_json']}")
print(f"  ❌ Erros                        : {corrections_log['resumo']['erros']}")
print(f"\nLog salvo em: {log_path}")
print("=" * 60)
