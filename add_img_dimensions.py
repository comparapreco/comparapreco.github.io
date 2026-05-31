
import os
import re
from bs4 import BeautifulSoup

def add_img_dimensions_robust(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    # Função auxiliar para processar tags <img>
    def process_img_tag(img_tag_str):
        nonlocal modified
        # Usar BeautifulSoup para parsear o fragmento da tag <img>
        img_soup = BeautifulSoup(img_tag_str, 'html.parser')
        img = img_soup.find('img')
        if img:
            if img.get('width') != '120' or img.get('height') != '120':
                img['width'] = '120'
                img['height'] = '120'
                modified = True
            
            new_style = 'width:100%;height:auto;'
            current_style = img.get('style', '')
            if new_style not in current_style:
                if current_style:
                    img['style'] = current_style + ';' + new_style
                else:
                    img['style'] = new_style
                modified = True
        return str(img_soup)

    # 1. Processar tags <img> diretas no HTML
    soup = BeautifulSoup(content, 'html.parser')
    for img in soup.find_all('img'):
        original_img_tag = str(img)
        processed_img_tag = process_img_tag(original_img_tag)
        if original_img_tag != processed_img_tag:
            img.replace_with(BeautifulSoup(processed_img_tag, 'html.parser'))
            modified = True
    
    if modified:
        content = str(soup)

    # 2. Processar tags <img> dentro de template literals JavaScript
    # Regex para encontrar template literals que contêm <img> tags
    # Isso é uma simplificação e pode não cobrir todos os casos complexos de JS
    # A regex busca por `...<img...>...`
    template_literal_pattern = re.compile(r'`([^`]*<img[^>]*>[^`]*)`')

    def replace_img_in_template_literal(match):
        nonlocal modified
        literal_content = match.group(1)
        # Regex para encontrar tags <img> dentro do conteúdo do template literal
        img_in_literal_pattern = re.compile(r'<img[^>]*>')

        def process_inner_img(inner_match):
            nonlocal modified
            original_inner_img_tag = inner_match.group(0)
            processed_inner_img_tag = process_img_tag(original_inner_img_tag)
            if original_inner_img_tag != processed_inner_img_tag:
                modified = True
            return processed_inner_img_tag

        new_literal_content = img_in_literal_pattern.sub(process_inner_img, literal_content)
        
        if new_literal_content != literal_content:
            return f'`{new_literal_content}`'
        return match.group(0)

    new_content = template_literal_pattern.sub(replace_img_in_template_literal, content)

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ Imagens em {file_path} atualizadas.")
    else:
        print(f"- Nenhuma alteração necessária em {file_path}.")

if __name__ == '__main__':
    with open('/home/ubuntu/html_files_to_correct.txt', 'r') as f:
        files = f.read().splitlines()

    for file in files:
        add_img_dimensions_robust(file)
