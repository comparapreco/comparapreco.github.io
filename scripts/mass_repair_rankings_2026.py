import os
import re
from pathlib import Path

def repair_rankings():
    root = Path('/home/ubuntu/comparapreco.github.io')
    rankings_dir = root / 'melhores-2026'
    
    # Mapeamento de categorias para pastas reais (alguns rankings usam nomes diferentes)
    category_map = {
        'gamer': 'games',
        'tecnologia': 'celulares', # Muitos itens de tecnologia estao em celulares ou outros
        'beleza': 'beleza',
        'casa': 'casa',
        'celulares': 'celulares',
        'eletrodomesticos': 'eletrodomesticos',
        'ferramentas': 'ferramentas',
        'games': 'games',
        'informatica': 'informatica',
        'moveis': 'moveis',
        'outros': 'outros',
        'tv-e-video': 'tv-e-video'
    }

    html_files = list(rankings_dir.glob('*.html'))
    
    for file_path in html_files:
        if file_path.name == 'index.html': continue
        
        content = file_path.read_text(errors='replace')
        
        # 1. Corrigir encoding comum
        content = content.replace('ElÃ©trica', 'Elétrica')
        content = content.replace('EletrÃ´nico', 'Eletrônico')
        content = content.replace('RemovÃ\xadvel', 'Removível')
        
        # 2. Corrigir links quebrados tentando encontrar o arquivo real
        links = set(re.findall(r'href="([^"]+)"', content))
        for link in links:
            if link.startswith('http') or link.startswith('#') or not link.startswith('../ofertas/'):
                continue
            
            link_path = (file_path.parent / link).resolve()
            if not link_path.exists():
                # Tentar encontrar o arquivo pelo ID (MLB...) ou parte do nome
                match = re.search(r'(MLB\d+|AMZ-[A-Z0-9]+)', link)
                if match:
                    item_id = match.group(1)
                    # Procurar em todas as subpastas de ofertas
                    found = list(root.glob(f'ofertas/*/*{item_id}*.html'))
                    if found:
                        new_link = '../' + str(found[0].relative_to(root))
                        content = content.replace(link, new_link)
                        print(f"Reparado em {file_path.name}: {link} -> {new_link}")
                    else:
                        # Se nao achou pelo ID, tenta pelo nome do arquivo sem a categoria
                        filename = Path(link).name
                        found_by_name = list(root.glob(f'ofertas/*/{filename}'))
                        if found_by_name:
                            new_link = '../' + str(found_by_name[0].relative_to(root))
                            content = content.replace(link, new_link)
                            print(f"Reparado por nome em {file_path.name}: {link} -> {new_link}")
                        else:
                            # Se ainda nao achou, redireciona para a categoria principal ou noticias
                            content = content.replace(link, '../noticias/')
                            print(f"Link perdido em {file_path.name}: {link} -> noticias")

        # 3. Substituir placeholders # por noticias
        content = content.replace('href="#"', 'href="../noticias/"')
        
        file_path.write_text(content)

if __name__ == "__main__":
    repair_rankings()
