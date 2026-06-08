import os
import re

ROOT_DIR = "/home/ubuntu/comparapreco.github.io"
AMAZON_TAG = "radar041-20"

def fix_amazon_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex para links da Amazon que não tem a tag correta
    # Procura por dp/ID e garante que a tag seja adicionada ou substituída
    new_content = re.sub(r'amazon\.com\.br/dp/([A-Z0-9]+)(\?[^"]*)?', 
                         f'amazon.com.br/dp/\\1?tag={AMAZON_TAG}', content)
    
    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

count = 0
for root, dirs, files in os.walk(os.path.join(ROOT_DIR, "ofertas")):
    for f in files:
        if f.endswith(".html"):
            if fix_amazon_in_file(os.path.join(root, f)):
                count += 1

print(f"Links da Amazon corrigidos em {count} arquivos.")
