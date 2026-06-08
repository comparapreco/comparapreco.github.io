import os
import re
from pathlib import Path

def optimize():
    root = Path('/home/ubuntu/comparapreco.github.io')
    
    for html_file in root.glob('**/*.html'):
        if 'node_modules' in str(html_file): continue
        
        content = html_file.read_text(errors='replace')
        
        # 1. Adicionar loading="lazy" em imagens que nao tem
        # Mas evitar na primeira imagem (LCP)
        imgs = re.findall(r'<img[^>]+>', content)
        for i, img in enumerate(imgs):
            if i == 0: continue # Pular a primeira para nao prejudicar LCP
            if 'loading=' not in img:
                new_img = img.replace('>', ' loading="lazy">')
                content = content.replace(img, new_img)
        
        # 2. Garantir que imagens tenham alt (usar o titulo da pagina se estiver vazio)
        title_match = re.search(r'<title>(.*?)</title>', content)
        page_title = title_match.group(1).split('|')[0].strip() if title_match else "Produto Compara Preço"
        
        content = content.replace('alt=""', f'alt="{page_title}"')
        
        html_file.write_text(content)

if __name__ == "__main__":
    optimize()
