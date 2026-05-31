#!/usr/bin/env python3.11
"""
Script automático para corrigir todas as páginas do site Radar
- Cria páginas faltantes (404)
- Remove menções a outras lojas (Amazon, Shopee, Americanas, etc)
- Garante que todos os links de afiliado apontam para Mercado Livre com matt_tool
- Atualiza o menu de navegação
"""

import os
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PAGES_TO_CREATE = {
    'quedas-hoje': {
        'title': 'Quedas de Preço Hoje — Produtos com Desconto | Compara Preço',
        'description': 'Produtos que tiveram queda de preço hoje no Mercado Livre. Veja os maiores descontos em tempo real.',
        'h1': '📉 Quedas de Preço Hoje',
        'subtitle': 'Produtos que ficaram mais baratos nas últimas 24 horas no Mercado Livre.',
        'emoji': '📉',
        'color_start': '#ef4444',
        'color_end': '#dc2626'
    },
    'ofertas-explodindo': {
        'title': 'Ofertas Explodindo — Descontos Incríveis | Compara Preço',
        'description': 'As ofertas mais explosivas do Mercado Livre. Produtos com desconto de até 70% com estoque limitado.',
        'h1': '💥 Ofertas Explodindo',
        'subtitle': 'As promoções mais agressivas do Mercado Livre com estoque limitado.',
        'emoji': '💥',
        'color_start': '#f59e0b',
        'color_end': '#d97706'
    },
    'central-comparativos': {
        'title': 'Central de Comparativos — Compare Produtos | Compara Preço',
        'description': 'Compare produtos lado a lado. Veja especificações, preços e avaliações de produtos similares no Mercado Livre.',
        'h1': '⚖️ Central de Comparativos',
        'subtitle': 'Compare produtos lado a lado e escolha o melhor custo-benefício.',
        'emoji': '⚖️',
        'color_start': '#8b5cf6',
        'color_end': '#7c3aed'
    },
    'radar-de-mercado': {
        'title': 'Radar de Mercado — Inteligência de Preços | Compara Preço',
        'description': 'Análise em tempo real do mercado. Veja tendências de preço, produtos em alta e oportunidades de compra no Mercado Livre.',
        'h1': '📡 Radar de Mercado',
        'subtitle': 'Inteligência de mercado em tempo real. Tendências, análises e oportunidades.',
        'emoji': '📡',
        'color_start': '#06b6d4',
        'color_end': '#0891b2'
    }
}

TEMPLATE_HTML = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{title}</title>
<meta content="{description}" name="description"/>
<link href="https://comparapreco.github.io/{slug}/" rel="canonical"/>
<link href="../assets/css/style.css" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet"/>
<style>
  .hero {{ background: linear-gradient(135deg, {color_start} 0%, {color_end} 100%); color: white; padding: 60px 0 40px; margin-bottom: 40px; }}
  .hero h1 {{ font-size: 2.5rem; margin-bottom: 15px; }}
  .hero p {{ opacity: 0.9; font-size: 1.1rem; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
  .filters {{ display: flex; gap: 10px; margin-bottom: 30px; flex-wrap: wrap; }}
  .filter-btn {{ padding: 8px 16px; border-radius: 20px; border: 2px solid var(--border); background: var(--card); cursor: pointer; transition: all 0.3s; font-weight: 600; }}
  .filter-btn.active, .filter-btn:hover {{ background: var(--primary); color: white; border-color: var(--primary); }}
  .products-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; margin-bottom: 40px; }}
  .product-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; transition: all 0.3s; }}
  .product-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
  .product-badge {{ background: #e11d48; color: white; padding: 4px 10px; font-size: 0.8rem; font-weight: 800; display: inline-block; border-radius: 4px; margin-bottom: 8px; }}
  .product-img {{ width: 100%; height: 200px; object-fit: contain; background: #f8f8f8; padding: 15px; }}
  .product-body {{ padding: 15px; }}
  .product-title {{ font-weight: 700; font-size: 0.95rem; margin-bottom: 8px; line-height: 1.4; }}
  .product-price {{ font-size: 1.4rem; font-weight: 800; color: #00a83f; margin-bottom: 12px; }}
  .btn-ml {{ display: block; background: #00a83f; color: white; text-align: center; padding: 12px; border-radius: 8px; font-weight: 700; text-decoration: none; transition: background 0.3s; }}
  .btn-ml:hover {{ background: #008f35; }}
  .section-title {{ font-size: 1.5rem; font-weight: 800; margin-bottom: 20px; border-left: 4px solid var(--primary); padding-left: 15px; }}
  .stats-bar {{ display: flex; gap: 30px; flex-wrap: wrap; margin-top: 20px; }}
  .stat-item {{ text-align: center; }}
  .stat-num {{ font-size: 2rem; font-weight: 800; }}
  .stat-label {{ font-size: 0.85rem; opacity: 0.8; }}
</style>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-P0X4Z9Y7B2"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-P0X4Z9Y7B2');
</script>
<script>
  document.addEventListener('DOMContentLoaded', function() {{
    document.querySelectorAll('a[href*="mercadolivre.com"]').forEach(function(link) {{
      link.addEventListener('click', function() {{
        gtag('event', 'affiliate_click', {{
          'event_category': 'engagement',
          'event_label': this.href,
          'link_url': this.href,
          'product_name': this.getAttribute('title') || this.innerText
        }});
      }});
    }});
  }});
</script>
<meta name="google-adsense-account" content="ca-pub-4896859041377751">
</head>
<body>
<header class="header">
<div class="container header-inner">
<a class="logo" href="../">📊 <strong>Compara Preço</strong></a>
<div class="search-bar">
<input id="searchInput" placeholder="Buscar ofertas..." type="text"/>
</div>
<button id="themeToggle">🌙</button>
</div>
</header>

<section class="hero">
<div class="container">
<div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 10px;"><a href="../" style="color:white; text-decoration:none;">Início</a> › {h1}</div>
<h1>{emoji} {h1}</h1>
<p>{subtitle}</p>
<div class="stats-bar">
  <div class="stat-item"><div class="stat-num">+500</div><div class="stat-label">Produtos</div></div>
  <div class="stat-item"><div class="stat-num">Até 70%</div><div class="stat-label">De Desconto</div></div>
  <div class="stat-item"><div class="stat-num">100%</div><div class="stat-label">Mercado Livre</div></div>
</div>
</div>
</section>

<main class="container">
<h2 class="section-title">{emoji} Destaques</h2>
<div class="products-grid" id="productsGrid">
  <!-- Carregado via JavaScript -->
</div>
<div style="text-align: center; margin: 40px 0;">
  <a href="https://www.mercadolivre.com.br/ofertas?matt_tool=vendas0nline" target="_blank" rel="noopener sponsored" class="btn-ml" style="display: inline-block; padding: 15px 40px; font-size: 1.1rem;">
    🛒 Ver Todas as Ofertas no Mercado Livre →
  </a>
</div>
</main>

<footer class="footer">
<div class="container">
<div class="footer-grid">
  <div class="footer-col">
    <h3>Compara Preço</h3>
    <p>Monitoramos as melhores ofertas do Mercado Livre para você economizar sempre.</p>
  </div>
  <div class="footer-col">
    <h4>Navegação</h4>
    <a href="../">Início</a>
    <a href="../noticias/">Blog</a>
    <a href="../melhores-2026/">Melhores de 2026</a>
    <a href="../mais-clicados/">Mais Clicados</a>
  </div>
  <div class="footer-col">
    <h4>Institucional</h4>
    <a href="../privacidade/">Privacidade</a>
    <a href="../termos/">Termos de Uso</a>
    <a href="../metodologia/">Metodologia</a>
    <a href="../disclaimer/">Disclaimer</a>
  </div>
</div>
<div class="footer-bottom">
  <p>© 2026 Compara Preço. Este site contém links de afiliado do Mercado Livre. Ao clicar e comprar, você nos ajuda a manter o site gratuito.</p>
</div>
</div>
</footer>
<script src="../assets/js/app.js"></script>
</body>
</html>'''

def create_missing_pages():
    """Cria as páginas que faltam (404)"""
    print("🔧 Criando páginas faltantes...")
    for slug, config in PAGES_TO_CREATE.items():
        page_dir = BASE_DIR / slug
        page_dir.mkdir(exist_ok=True)
        
        index_file = page_dir / 'index.html'
        if not index_file.exists():
            html = TEMPLATE_HTML.format(
                slug=slug,
                title=config['title'],
                description=config['description'],
                h1=config['h1'],
                subtitle=config['subtitle'],
                emoji=config['emoji'],
                color_start=config['color_start'],
                color_end=config['color_end']
            )
            index_file.write_text(html, encoding='utf-8')
            print(f"  ✅ Criada: /{slug}/")
        else:
            print(f"  ⏭️  Já existe: /{slug}/")

def remove_other_stores(html_content):
    """Remove menções a outras lojas e deixa apenas Mercado Livre"""
    # Lista de padrões a remover
    patterns_to_remove = [
        # Amazon
        (r'<li><strong>Amazon:</strong>.*?</li>', ''),
        (r'Amazon Prime Day', 'Promoções do Mercado Livre'),
        (r'Amazon Prime', 'Mercado Livre'),
        (r'prime day', 'promoções'),
        (r'amazon\.com\.br', 'mercadolivre.com.br'),
        
        # Shopee
        (r'<li><strong>Shopee:</strong>.*?</li>', ''),
        (r'shopee\.com\.br', 'mercadolivre.com.br'),
        
        # Americanas
        (r'<li><strong>Americanas:</strong>.*?</li>', ''),
        (r'americanas\.com\.br', 'mercadolivre.com.br'),
        
        # Magazine Luiza
        (r'magazine luiza', 'Mercado Livre'),
        (r'magalu\.com\.br', 'mercadolivre.com.br'),
        
        # Genérico
        (r'Mercado Livre, Amazon, Shopee e Americanas', 'Mercado Livre'),
        (r'Mercado Livre, Amazon, Shopee', 'Mercado Livre'),
        (r'Use o Compara Preço para comparar preços em tempo real no Mercado Livre, Amazon, Shopee e Americanas', 'Use o Compara Preço para comparar preços em tempo real no Mercado Livre'),
        (r'Use o Compara Preço para comparar preços em tempo real em.*?lojas', 'Use o Compara Preço para acompanhar as melhores ofertas do Mercado Livre'),
    ]
    
    result = html_content
    for pattern, replacement in patterns_to_remove:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE | re.DOTALL)
    
    return result

def ensure_affiliate_links(html_content):
    """Garante que todos os links do Mercado Livre têm matt_tool=vendas0nline"""
    # Padrão para encontrar links do Mercado Livre
    pattern = r'href="(https://www\.mercadolivre\.com\.br/[^"]*)"'
    
    def add_matt_tool(match):
        url = match.group(1)
        # Se já tem matt_tool, não adiciona novamente
        if 'matt_tool' in url:
            return f'href="{url}"'
        # Adiciona matt_tool
        separator = '&' if '?' in url else '?'
        return f'href="{url}{separator}matt_tool=vendas0nline"'
    
    result = re.sub(pattern, add_matt_tool, html_content)
    return result

def fix_html_files():
    """Corrige todos os arquivos HTML do site"""
    print("\n🔧 Corrigindo arquivos HTML...")
    
    html_files = list(BASE_DIR.glob('**/*.html'))
    fixed_count = 0
    
    for html_file in html_files:
        # Pular arquivos de template e git
        if '.git' in str(html_file) or 'templates' in str(html_file):
            continue
        
        try:
            content = html_file.read_text(encoding='utf-8')
            original_content = content
            
            # Remover outras lojas
            content = remove_other_stores(content)
            
            # Garantir links de afiliado
            content = ensure_affiliate_links(content)
            
            # Se mudou, salvar
            if content != original_content:
                html_file.write_text(content, encoding='utf-8')
                fixed_count += 1
                rel_path = html_file.relative_to(BASE_DIR)
                print(f"  ✅ Corrigido: {rel_path}")
        
        except Exception as e:
            print(f"  ❌ Erro em {html_file}: {e}")
    
    print(f"\n✅ Total de arquivos corrigidos: {fixed_count}")

def update_navigation():
    """Atualiza o menu de navegação em todos os arquivos"""
    print("\n🧭 Atualizando menu de navegação...")
    
    # Menu correto com URLs reais
    correct_menu_urls = {
        'ofertas-hoje': '/ofertas-hoje/',
        'melhores-2026': '/melhores-2026/',
        'premio-radar-2026': '/premio-radar-2026/',
        'quedas-hoje': '/quedas-hoje/',
        'mais-clicados': '/mais-clicados/',
        'ofertas-explodindo': '/ofertas-explodindo/',
        'central-comparativos': '/central-comparativos/',
        'comparar': '/comparar/',
        'marcas': '/marcas/',
        'radar-de-mercado': '/radar-de-mercado/',
        'tendencias': '/tendencias/',
        'metodologia': '/metodologia/',
        'noticias': '/noticias/',
        'guias': '/guias/',
        'glossario': '/glossario/',
        'aprender': '/aprender/',
        'vale-a-pena-esperar': '/vale-a-pena-esperar/',
        'calendario-de-precos': '/calendario-de-precos/',
    }
    
    # URLs incorretas que precisam ser corrigidas
    incorrect_urls = {
        '/ofertas-hoje/': '/ofertas-hoje/',
        '/premio-compara-2026/': '/premio-radar-2026/',
        '/premio-radar-2026/': '/premio-radar-2026/',
        '/quedas-hoje/': '/quedas-hoje/',
        '/explodindo/': '/ofertas-explodindo/',
        '/comparativos/': '/central-comparativos/',
        '/monitor-de-mercado/': '/radar-de-mercado/',
        '/o-que-esta-em-alta/': '/tendencias/',
    }
    
    html_files = list(BASE_DIR.glob('**/*.html'))
    updated_count = 0
    
    for html_file in html_files:
        if '.git' in str(html_file):
            continue
        
        try:
            content = html_file.read_text(encoding='utf-8')
            original_content = content
            
            # Corrigir URLs incorretas
            for old_url, new_url in incorrect_urls.items():
                content = content.replace(f'href="{old_url}"', f'href="{new_url}"')
                content = content.replace(f"href='{old_url}'", f"href='{new_url}'")
            
            if content != original_content:
                html_file.write_text(content, encoding='utf-8')
                updated_count += 1
        
        except Exception as e:
            print(f"  ❌ Erro em {html_file}: {e}")
    
    print(f"✅ Menu atualizado em {updated_count} arquivos")

def main():
    """Executa todas as correções"""
    print("=" * 60)
    print("🚀 INICIANDO CORREÇÃO AUTOMÁTICA DO SITE RADAR")
    print("=" * 60)
    
    create_missing_pages()
    fix_html_files()
    update_navigation()
    
    print("\n" + "=" * 60)
    print("✅ TODAS AS CORREÇÕES CONCLUÍDAS!")
    print("=" * 60)
    print("\n📋 Resumo:")
    print("  ✅ Páginas faltantes criadas")
    print("  ✅ Menções a outras lojas removidas")
    print("  ✅ Links de afiliado garantidos com matt_tool")
    print("  ✅ Menu de navegação atualizado")
    print("\n🔗 Próximos passos:")
    print("  1. Fazer commit das mudanças: git add -A && git commit -m 'Fix: Corrigir todas as páginas'")
    print("  2. Fazer push: git push origin main")
    print("  3. Verificar o site em produção")

if __name__ == '__main__':
    main()
