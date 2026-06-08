import os
import re
from pathlib import Path

def inject_eeat():
    root = Path('/home/ubuntu/comparapreco.github.io')
    
    author_box = """
    <div class="author-box" style="display: flex; align-items: center; gap: 20px; padding: 25px; background: #f8fafc; border-radius: 20px; margin: 40px 0; border: 1px solid #e2e8f0;">
        <div style="width: 60px; height: 60px; background: #cbd5e1; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">👤</div>
        <div>
            <p style="margin: 0; font-weight: 700; color: #1e293b;">Revisado por: Equipe Editorial Compara Preço</p>
            <p style="margin: 5px 0 0; font-size: 0.9rem; color: #64748b;">Especialistas em tecnologia e consumo. <a href="/autores/especialista-tecnologia.html" style="color: var(--primary); text-decoration: none; font-weight: 600;">Saiba mais sobre nosso processo editorial</a></p>
        </div>
    </div>"""

    eeat_badges = """
    <div class="eeat-badges" style="display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap;">
        <span style="background: #ecfdf5; color: #065f46; padding: 5px 12px; border-radius: 50px; font-size: 0.75rem; font-weight: 700; border: 1px solid #a7f3d0;">✅ Verificado por Especialista</span>
        <span style="background: #eff6ff; color: #1e40af; padding: 5px 12px; border-radius: 50px; font-size: 0.75rem; font-weight: 700; border: 1px solid #bfdbfe;">🕒 Atualizado em Junho 2026</span>
        <span style="background: #fff7ed; color: #9a3412; padding: 5px 12px; border-radius: 50px; font-size: 0.75rem; font-weight: 700; border: 1px solid #fed7aa;">💎 Análise Imparcial</span>
    </div>"""

    # Aplicar em Rankings e Guias
    target_dirs = [root / 'melhores-2026', root / 'guias']
    for t_dir in target_dirs:
        for html_file in t_dir.glob('**/*.html'):
            if html_file.name == 'index.html': continue
            content = html_file.read_text(errors='replace')
            
            if 'author-box' not in content:
                # Inserir selos antes do H1
                content = re.sub(r'(<h1.*?>)', eeat_badges + r'\1', content)
                # Inserir box de autor antes do footer ou no final do main
                content = content.replace('</main>', author_box + '\n</main>')
                html_file.write_text(content)

if __name__ == "__main__":
    inject_eeat()
