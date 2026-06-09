#!/usr/bin/env python3.11
"""
Script avançado para corrigir completamente o site
- Remove TODAS as menções a outras lojas
- Adiciona matt_tool a TODOS os links do Mercado Livre
- Corrige páginas específicas (cupons, política de afiliados, vendedor)
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

BASE_DIR = Path(__file__).parent.parent

def add_matt_tool_to_url(url):
    """Adiciona matt_tool=60566305 a uma URL do Mercado Livre"""
    if 'matt_tool' in url:
        return url
    
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params['matt_tool'] = ['60566305']
    
    new_query = urlencode({k: v[0] for k, v in params.items()})
    new_url = urlunparse(parsed._replace(query=new_query))
    return new_url

def fix_all_affiliate_links(html_content):
    """Adiciona matt_tool a todos os links do Mercado Livre"""
    # Padrão para encontrar href com URLs do Mercado Livre
    pattern = r'href="(https://www\.mercadolivre\.com\.br/[^"]*)"'
    
    def replace_url(match):
        url = match.group(1)
        new_url = add_matt_tool_to_url(url)
        return f'href="{new_url}"'
    
    result = re.sub(pattern, replace_url, html_content)
    return result

def remove_all_other_stores(html_content):
    """Remove TODAS as menções a outras lojas"""
    
    # Padrões mais agressivos para remover outras lojas
    patterns = [
        # Cupons de outras lojas
        (r'<button[^>]*data-filter="amazon"[^>]*>.*?</button>', ''),
        (r'<button[^>]*data-filter="shopee"[^>]*>.*?</button>', ''),
        (r'<button[^>]*data-filter="americanas"[^>]*>.*?</button>', ''),
        
        # Descrições de cupons
        (r'store:\s*[\'"]Amazon[\'"],.*?description:\s*[\'"][^\'"]*[\'"],', ''),
        (r'store:\s*[\'"]Shopee[\'"],.*?description:\s*[\'"][^\'"]*[\'"],', ''),
        (r'store:\s*[\'"]Americanas[\'"],.*?description:\s*[\'"][^\'"]*[\'"],', ''),
        
        # Divs de lojas
        (r'<div[^>]*class="store-name"[^>]*>Shopee</div>', ''),
        (r'<div[^>]*class="store-name"[^>]*>Americanas</div>', ''),
        (r'<div[^>]*class="store-name"[^>]*>Amazon</div>', ''),
        
        # Descrições meta
        (r'Cupons e códigos de desconto para Mercado Livre, Amazon, Magalu e outras lojas\.', 'Cupons e códigos de desconto para Mercado Livre.'),
        (r'Cupons exclusivos para Mercado Livre, Amazon, Magalu e outras lojas\.', 'Cupons exclusivos para Mercado Livre.'),
        
        # Parágrafos inteiros
        (r'<p>Cupons exclusivos para Mercado Livre, Amazon, Magalu e outras lojas\. Economize ainda mais nas suas compras\.</p>', 
         '<p>Cupons exclusivos para Mercado Livre. Economize ainda mais nas suas compras.</p>'),
        
        # Tabelas de políticas de afiliados
        (r'<tr>.*?<strong>Amazon</strong>.*?</tr>', ''),
        (r'<tr>.*?<strong>Shopee</strong>.*?</tr>', ''),
        (r'<tr>.*?<strong>Americanas</strong>.*?</tr>', ''),
        (r'<tr>.*?<strong>Magazine Luiza</strong>.*?</tr>', ''),
        (r'<tr>.*?<strong>Magalu</strong>.*?</tr>', ''),
        
        # Referências genéricas
        (r'Amazon Afiliados', 'Mercado Livre'),
        (r'Shopee Afiliados', 'Mercado Livre'),
        (r'Americanas Afiliados', 'Mercado Livre'),
        (r'Magalu Afiliados', 'Mercado Livre'),
    ]
    
    result = html_content
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE | re.DOTALL)
    
    return result

def fix_specific_files():
    """Corrige arquivos específicos que precisam de atenção especial"""
    
    print("🔧 Corrigindo arquivos específicos...")
    
    # Corrigir cupons/index.html
    cupons_file = BASE_DIR / 'cupons' / 'index.html'
    if cupons_file.exists():
        content = cupons_file.read_text(encoding='utf-8')
        original = content
        
        # Remover filtros de outras lojas
        content = re.sub(r'<button[^>]*class="filter-btn"[^>]*data-filter="(amazon|shopee|americanas)"[^>]*>.*?</button>', '', content, flags=re.DOTALL)
        
        # Remover dados de cupons de outras lojas
        content = re.sub(r'\{\s*store:\s*[\'"](?:Amazon|Shopee|Americanas|Magalu)[\'"],.*?\},', '', content, flags=re.DOTALL)
        
        # Atualizar descrição
        content = content.replace(
            'Cupons e códigos de desconto para Mercado Livre, Amazon, Magalu e outras lojas',
            'Cupons e códigos de desconto para Mercado Livre'
        )
        
        if content != original:
            cupons_file.write_text(content, encoding='utf-8')
            print("  ✅ Corrigido: cupons/index.html")
    
    # Corrigir politica-afiliados/index.html
    politica_file = BASE_DIR / 'politica-afiliados' / 'index.html'
    if politica_file.exists():
        content = politica_file.read_text(encoding='utf-8')
        original = content
        
        # Remover linhas de tabela com outras lojas
        content = re.sub(r'<tr>.*?<td><strong>(?:Amazon|Shopee|Americanas|Magazine Luiza|Magalu)</strong></td>.*?</tr>', '', content, flags=re.DOTALL)
        
        if content != original:
            politica_file.write_text(content, encoding='utf-8')
            print("  ✅ Corrigido: politica-afiliados/index.html")
    
    # Corrigir vendedor/index.html
    vendedor_file = BASE_DIR / 'vendedor' / 'index.html'
    if vendedor_file.exists():
        content = vendedor_file.read_text(encoding='utf-8')
        original = content
        
        # Remover divs de outras lojas
        content = re.sub(r'<div[^>]*class="store-name"[^>]*>(?:Shopee|Americanas|Amazon)</div>', '', content)
        
        if content != original:
            vendedor_file.write_text(content, encoding='utf-8')
            print("  ✅ Corrigido: vendedor/index.html")

def process_all_html_files():
    """Processa todos os arquivos HTML do site"""
    
    print("\n🔧 Processando todos os arquivos HTML...")
    
    html_files = list(BASE_DIR.glob('**/*.html'))
    processed = 0
    
    for html_file in html_files:
        if '.git' in str(html_file) or 'templates' in str(html_file):
            continue
        
        try:
            content = html_file.read_text(encoding='utf-8')
            original = content
            
            # Adicionar matt_tool a todos os links
            content = fix_all_affiliate_links(content)
            
            # Remover outras lojas
            content = remove_all_other_stores(content)
            
            if content != original:
                html_file.write_text(content, encoding='utf-8')
                processed += 1
                rel_path = html_file.relative_to(BASE_DIR)
                print(f"  ✅ Processado: {rel_path}")
        
        except Exception as e:
            print(f"  ❌ Erro em {html_file}: {e}")
    
    print(f"\n✅ Total de arquivos processados: {processed}")

def main():
    print("=" * 70)
    print("🚀 INICIANDO CORREÇÃO AVANÇADA DO SITE RADAR")
    print("=" * 70)
    
    fix_specific_files()
    process_all_html_files()
    
    print("\n" + "=" * 70)
    print("✅ CORREÇÃO AVANÇADA CONCLUÍDA!")
    print("=" * 70)
    print("\n📋 O que foi feito:")
    print("  ✅ Removidas TODAS as menções a outras lojas")
    print("  ✅ Adicionado matt_tool a TODOS os links do Mercado Livre")
    print("  ✅ Corrigidos arquivos específicos (cupons, política, vendedor)")
    print("\n🔗 Próximos passos:")
    print("  1. git add -A")
    print("  2. git commit -m 'Fix: Remover todas as lojas, adicionar matt_tool a todos os links'")
    print("  3. git push origin main")

if __name__ == '__main__':
    main()
