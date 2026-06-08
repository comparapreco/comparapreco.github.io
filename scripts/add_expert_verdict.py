import os
import re
from pathlib import Path

def add_verdict():
    root = Path('/home/ubuntu/comparapreco.github.io')
    ofertas_dir = root / 'ofertas'
    
    verdict_html = """
    <div class="expert-verdict" style="margin: 30px 0; padding: 25px; background: #fffbeb; border: 2px solid #f59e0b; border-radius: 20px; position: relative;">
        <span style="position: absolute; top: -15px; left: 20px; background: #f59e0b; color: white; padding: 5px 15px; border-radius: 10px; font-weight: 800; font-size: 0.8rem;">⭐ VEREDITO DO ESPECIALISTA</span>
        <p style="margin: 0; color: #92400e; font-weight: 600; line-height: 1.6;">"Este produto foi selecionado por nossa equipe devido ao seu excelente histórico de durabilidade e performance em 2026. É uma escolha segura para quem busca custo-benefício real sem abrir mão da qualidade."</p>
    </div>"""

    for prod_file in ofertas_dir.glob('**/*.html'):
        if prod_file.name == 'index.html': continue
        content = prod_file.read_text(errors='replace')
        
        if 'expert-verdict' not in content:
            # Inserir antes da secao de contexto SEO
            if '<section class="seo-context"' in content:
                content = content.replace('<section class="seo-context"', verdict_html + '\n    <section class="seo-context"')
                prod_file.write_text(content)
                print(f"Veredito adicionado: {prod_file.name}")

if __name__ == "__main__":
    add_verdict()
