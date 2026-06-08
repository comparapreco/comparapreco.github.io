import os
import re
from pathlib import Path

def add_ctas():
    root = Path('/home/ubuntu/comparapreco.github.io')
    ofertas_dir = root / 'ofertas'
    
    # CSS para o CTA flutuante
    cta_style = """
    <style>
        .floating-cta {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 400px;
            background: #00c853;
            color: white;
            padding: 15px 25px;
            border-radius: 50px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 10px 25px rgba(0, 200, 83, 0.4);
            z-index: 1000;
            text-decoration: none;
            font-weight: 800;
            transition: all 0.3s ease;
        }
        .floating-cta:hover { transform: translateX(-50%) translateY(-5px); background: #00a844; }
        @media (min-width: 768px) { .floating-cta { bottom: 30px; } }
    </style>"""

    for prod_file in ofertas_dir.glob('**/*.html'):
        if prod_file.name == 'index.html': continue
        content = prod_file.read_text(errors='replace')
        
        if 'floating-cta' not in content:
            # Pegar o link de oferta real
            link_match = re.search(r'href="(https://www\.mercadolivre\.com\.br/[^"]+)"', content)
            if not link_match:
                link_match = re.search(r'href="([^"]+)"', content) # Fallback para qualquer link
            
            if link_match:
                offer_url = link_match.group(1)
                cta_html = f"""
    <a href="{offer_url}" class="floating-cta" target="_blank" rel="nofollow">
        <span>🔥 Verificar Melhor Preço</span>
        <span>➜</span>
    </a>"""
                
                content = content.replace('</head>', cta_style + '\n</head>')
                content = content.replace('</body>', cta_html + '\n</body>')
                prod_file.write_text(content)
                print(f"CTA adicionado: {prod_file.name}")

if __name__ == "__main__":
    add_ctas()
