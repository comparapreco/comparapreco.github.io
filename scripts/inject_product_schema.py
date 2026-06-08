import os
import re
import json
from pathlib import Path

def inject_schema():
    root = Path('/home/ubuntu/comparapreco.github.io')
    ofertas_dir = root / 'ofertas'
    
    for prod_file in ofertas_dir.glob('**/*.html'):
        if prod_file.name == 'index.html': continue
        
        content = prod_file.read_text(errors='replace')
        
        # 1. Extrair dados básicos do HTML existente
        title_match = re.search(r'<title>(.*?)</title>', content)
        name = title_match.group(1).split('|')[0].strip() if title_match else "Produto"
        
        price_match = re.search(r'R\$\s?([\d.,]+)', content)
        price = price_match.group(1).replace('.', '').replace(',', '.') if price_match else "0.00"
        
        img_match = re.search(r'<img[^>]+src="([^"]+)"', content)
        image = img_match.group(1) if img_match else ""
        if image and not image.startswith('http'):
            # Tentar converter caminho relativo para absoluto do site
            image = "https://comparapreco.github.io/" + image.replace('../', '')

        # Tentar pegar o ID (MLB...)
        id_match = re.search(r'(MLB\d+)', prod_file.name)
        sku = id_match.group(1) if id_match else "SKU-PRODUTO"

        # 2. Gerar JSON-LD
        schema_data = {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": name,
            "image": [image] if image else [],
            "description": f"Confira a melhor oferta de {name} no Compara Preço. Preços atualizados e links diretos.",
            "sku": sku,
            "brand": {
                "@type": "Brand",
                "name": name.split()[0] # Estimativa da marca pela primeira palavra
            },
            "offers": {
                "@type": "Offer",
                "url": f"https://comparapreco.github.io/ofertas/{prod_file.relative_to(ofertas_dir)}",
                "priceCurrency": "BRL",
                "price": price,
                "availability": "https://schema.org/InStock",
                "itemCondition": "https://schema.org/NewCondition"
            }
        }
        
        schema_json = json.dumps(schema_data, indent=2, ensure_ascii=False)
        schema_html = f'\n  <script type="application/ld+json">\n{schema_json}\n  </script>'
        
        # 3. Inserir no Head se nao existir
        if 'application/ld+json' not in content:
            content = content.replace('</head>', schema_html + '\n</head>')
            prod_file.write_text(content)
            print(f"Schema injetado: {prod_file.name}")

if __name__ == "__main__":
    inject_schema()
