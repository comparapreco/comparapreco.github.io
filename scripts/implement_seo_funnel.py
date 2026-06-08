import os
import re
from pathlib import Path

def implement_seo_funnel():
    root = Path('/home/ubuntu/comparapreco.github.io')
    
    # 1. Mapeamento de Categorias e Rankings
    categories = {
        'beleza': 'melhores-beleza-2026.html',
        'casa': 'melhores-casa-2026.html',
        'celulares': 'melhores-celulares-2026.html',
        'eletrodomesticos': 'melhores-eletrodomesticos-2026.html',
        'ferramentas': 'melhores-ferramentas-2026.html',
        'gamer': 'melhores-gamer-2026.html',
        'games': 'melhores-games-2026.html',
        'informatica': 'melhores-informatica-2026.html',
        'moveis': 'melhores-moveis-2026.html',
        'tv-e-video': 'melhores-tv-e-video-2026.html',
        'outros': 'melhores-outros-2026.html'
    }

    # 2. Atualizar Páginas de Produto (Nível 3)
    # Adicionar breadcrumbs e links para categoria e ranking
    ofertas_dir = root / 'ofertas'
    for cat_dir in ofertas_dir.iterdir():
        if not cat_dir.is_dir(): continue
        cat_name = cat_dir.name
        ranking_file = categories.get(cat_name)
        
        for prod_file in cat_dir.glob('*.html'):
            if prod_file.name == 'index.html': continue
            
            content = prod_file.read_text(errors='replace')
            
            # Gerar Breadcrumbs
            breadcrumb_html = f"""
    <nav class="breadcrumb" style="margin-bottom: 20px; font-size: 0.9rem; color: #64748b;">
        <a href="../../" style="color: var(--primary); text-decoration: none;">Home</a> / 
        <a href="../../categorias/{cat_name}/" style="color: var(--primary); text-decoration: none;">{cat_name.capitalize()}</a> / 
        {ranking_file and f'<a href="../../melhores-2026/{ranking_file}" style="color: var(--primary); text-decoration: none;">Ranking 2026</a> / ' or ''}
        <span style="color: #94a3b8;">Produto</span>
    </nav>"""
            
            # Inserir breadcrumb após o header ou no início do body
            if '<nav class="breadcrumb"' not in content:
                content = re.sub(r'(<header.*?</header>)', r'\1' + breadcrumb_html, content, flags=re.DOTALL)
            
            # Adicionar links de contexto no final do conteúdo (antes do footer)
            context_links = f"""
    <section class="seo-context" style="margin-top: 40px; padding: 20px; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;">
        <h3 style="font-size: 1.1rem; margin-bottom: 15px; color: #1e293b;">Explorar mais em {cat_name.capitalize()}:</h3>
        <ul style="list-style: none; padding: 0; display: flex; gap: 20px; flex-wrap: wrap;">
            <li><a href="../../categorias/{cat_name}/" style="color: var(--primary); font-weight: 600;">Ver categoria completa</a></li>
            {ranking_file and f'<li><a href="../../melhores-2026/{ranking_file}" style="color: var(--primary); font-weight: 600;">Ranking Melhores de 2026</a></li>' or ''}
            <li><a href="../../noticias/" style="color: var(--primary); font-weight: 600;">Últimas notícias</a></li>
        </ul>
    </section>"""
            
            if '<section class="seo-context"' not in content:
                content = re.sub(r'(</main>|</footer>)', context_links + r'\1', content, count=1)
            
            prod_file.write_text(content)

    # 3. Atualizar Rankings (Nível 2)
    # Adicionar links para Guias Relacionados
    rankings_dir = root / 'melhores-2026'
    for ranking_file in rankings_dir.glob('*.html'):
        if ranking_file.name == 'index.html': continue
        content = ranking_file.read_text(errors='replace')
        
        # Linkar para guias (exemplo genérico por enquanto)
        guia_link = f"""
    <div class="guia-relacionado" style="margin: 20px 0; padding: 15px; border-left: 4px solid var(--primary); background: #f0fdf4;">
        <strong>Dica de Compra:</strong> Confira nosso <a href="../guias/" style="color: var(--primary); font-weight: 700;">Guia Completo de Compras Online</a> para economizar ainda mais em 2026.
    </div>"""
        
        if '<div class="guia-relacionado"' not in content:
            content = re.sub(r'(<h1.*?>.*?</h1>)', r'\1' + guia_link, content, flags=re.DOTALL)
        
        ranking_file.write_text(content)

    # 4. Atualizar Guias (Nível 1)
    # Linkar para pelo menos 3 rankings
    guias_dir = root / 'guias'
    for guia_file in guias_dir.glob('**/*.html'):
        content = guia_file.read_text(errors='replace')
        
        internal_links = """
    <div class="seo-funnel-links" style="margin-top: 40px; padding: 25px; background: #f1f5f9; border-radius: 16px;">
        <h3 style="margin-bottom: 15px;">Rankings Recomendados:</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            <a href="../../melhores-2026/melhores-celulares-2026.html" style="text-decoration:none; color:var(--secondary); font-weight:700;">📱 Top Celulares 2026</a>
            <a href="../../melhores-2026/melhores-eletrodomesticos-2026.html" style="text-decoration:none; color:var(--secondary); font-weight:700;">🔌 Eletrodomésticos</a>
            <a href="../../melhores-2026/melhores-informatica-2026.html" style="text-decoration:none; color:var(--secondary); font-weight:700;">💻 Informática</a>
        </div>
    </div>"""
        
        if '<div class="seo-funnel-links"' not in content:
            content = re.sub(r'(</main>|</body>)', internal_links + r'\1', content, count=1)
        
        guia_file.write_text(content)

if __name__ == "__main__":
    implement_seo_funnel()
