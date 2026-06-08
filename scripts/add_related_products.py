import os
import re
from pathlib import Path

def add_related():
    root = Path('/home/ubuntu/comparapreco.github.io')
    ofertas_dir = root / 'ofertas'
    
    for cat_dir in ofertas_dir.iterdir():
        if not cat_dir.is_dir(): continue
        
        # Pegar alguns produtos da mesma categoria para usar como relacionados
        related_files = list(cat_dir.glob('*.html'))[:3]
        related_links = ""
        for rf in related_files:
            if rf.name == 'index.html': continue
            content_rf = rf.read_text(errors='replace')
            title_match = re.search(r'<title>(.*?)</title>', content_rf)
            title = title_match.group(1).split('|')[0].strip() if title_match else "Ver produto"
            related_links += f'<li><a href="{rf.name}" style="color: var(--primary); text-decoration: none;">➜ {title}</a></li>\n'

        widget_html = f"""
    <div class="related-products" style="margin-top: 40px; padding: 25px; background: #fff; border: 1px solid #e2e8f0; border-radius: 20px;">
        <h3 style="margin-bottom: 15px; font-size: 1.2rem;">Produtos Relacionados:</h3>
        <ul style="list-style: none; padding: 0; line-height: 2;">
            {related_links}
        </ul>
    </div>"""

        for prod_file in cat_dir.glob('*.html'):
            if prod_file.name == 'index.html': continue
            content = prod_file.read_text(errors='replace')
            
            if 'related-products' not in content:
                # Inserir antes do footer ou no final do main
                content = content.replace('</main>', widget_html + '\n</main>')
                prod_file.write_text(content)

if __name__ == "__main__":
    add_related()
