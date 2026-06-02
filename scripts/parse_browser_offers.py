import re
import json
import os
import sys

def parse_markdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex para encontrar produtos no markdown do browser
    # Exemplo: [Nome](Link) ... ~~R$PreçoAntigo~~ ... R$PreçoAtual ... % OFF
    products = []
    
    # O markdown do browser costuma agrupar o link e o nome
    # [Notebook Gamer Asus...](https://www.mercadolivre.com.br/...)
    link_pattern = r'\[([^\]]+)\]\((https://www\.mercadolivre\.com\.br/[^\)]+)\)'
    matches = re.finditer(link_pattern, content)
    
    for match in matches:
        name = match.group(1).strip()
        url = match.group(2).strip()
        
        # Tenta extrair o ID do MLB da URL
        mlb_id_match = re.search(r'MLB-?(\d+)', url)
        if not mlb_id_match:
            mlb_id_match = re.search(r'wid=MLB(\d+)', url)
            
        mlb_id = f"MLB{mlb_id_match.group(1)}" if mlb_id_match else f"GEN{hash(url) % 10000000}"
        
        # Busca o preço próximo ao link no texto
        # Procuramos por R$ seguido de números após o link
        start_pos = match.end()
        end_pos = start_pos + 500 # Olha os próximos 500 caracteres
        context = content[start_pos:end_pos]
        
        prices = re.findall(r'R\$\s?([\d\.]+)', context)
        current_price = 0
        old_price = 0
        
        if len(prices) >= 2:
            old_price = float(prices[0].replace('.', ''))
            current_price = float(prices[1].replace('.', ''))
        elif len(prices) == 1:
            current_price = float(prices[0].replace('.', ''))
            old_price = current_price * 1.2 # Fallback
            
        if current_price > 0:
            products.append({
                "id": mlb_id,
                "name": name,
                "price": current_price,
                "original_price": old_price,
                "permalink": url,
                "status": "active"
            })
            
    return products

if __name__ == "__main__":
    md_file = "/home/ubuntu/page_texts/www.mercadolivre.com.br_ofertas.md"
    if not os.path.exists(md_file):
        # Tenta o outro nome de arquivo gerado
        md_file = "/home/ubuntu/page_texts/www.mercadolivre.com.br_ofertas_c_id__home_navigation_desktop_promotions_category-deals_electronics_.md"
        
    if os.path.exists(md_file):
        prods = parse_markdown(md_file)
        print(json.dumps(prods, indent=2, ensure_ascii=False))
    else:
        print("[]")
