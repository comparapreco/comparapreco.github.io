import os
import re
from pathlib import Path

def audit_rankings():
    root = Path('/home/ubuntu/comparapreco.github.io')
    rankings_dir = root / 'melhores-2026'
    
    if not rankings_dir.exists():
        print(f"Erro: Diretorio {rankings_dir} nao encontrado.")
        return

    html_files = list(rankings_dir.glob('*.html'))
    report = []
    
    print(f"Auditoria de Rankings 2026 - Encontrados {len(html_files)} arquivos.\n")
    
    for file_path in html_files:
        content = file_path.read_text(errors='replace')
        
        # Verificar links quebrados (href)
        links = re.findall(r'href="([^"]+)"', content)
        broken_links = []
        for link in links:
            if link.startswith('http') or link.startswith('#') or link.startswith('mailto:'):
                continue
            
            # Resolver caminho relativo
            link_path = (file_path.parent / link).resolve()
            if not link_path.exists():
                broken_links.append(link)
        
        # Verificar imagens quebradas (src)
        images = re.findall(r'src="([^"]+)"', content)
        broken_images = []
        for img in images:
            if img.startswith('http') or img.startswith('data:'):
                continue
            img_path = (file_path.parent / img).resolve()
            if not img_path.exists():
                broken_images.append(img)
                
        # Verificar placeholders (#)
        placeholders = content.count('href="#"')
        
        # Verificar encoding corrompido (caracteres comuns de erro)
        encoding_issues = re.findall(r'[ÃÂÁÉÍÓÚãâáéíóú]{2,}', content)
        
        if broken_links or broken_images or placeholders > 0 or encoding_issues:
            report.append({
                'file': file_path.name,
                'broken_links': broken_links,
                'broken_images': broken_images,
                'placeholders': placeholders,
                'encoding_issues': list(set(encoding_issues))
            })

    if not report:
        print("Nenhum problema critico encontrado nos rankings.")
    else:
        for item in report:
            print(f"Arquivo: {item['file']}")
            if item['broken_links']: print(f"  - Links quebrados: {item['broken_links']}")
            if item['broken_images']: print(f"  - Imagens quebradas: {item['broken_images']}")
            if item['placeholders']: print(f"  - Placeholders (#): {item['placeholders']}")
            if item['encoding_issues']: print(f"  - Possivel erro encoding: {item['encoding_issues']}")
            print("-" * 30)

if __name__ == "__main__":
    audit_rankings()
