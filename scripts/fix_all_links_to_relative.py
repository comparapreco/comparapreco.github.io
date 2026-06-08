import os
import re

def fix_links_in_file(filepath, depth):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Prefixo relativo baseado na profundidade do arquivo
    rel_prefix = "../" * depth if depth > 0 else "./"
    
    # Substituir href="/..." por href="rel_prefix..."
    # Mas ignorar links externos (http://, https://) e links que já são relativos
    def replace_link(match):
        link = match.group(1)
        if link.startswith('/') and not link.startswith('//'):
            new_link = rel_prefix + link.lstrip('/')
            return f'href="{new_link}"'
        return match.group(0)

    new_content = re.sub(r'href="(/[^"]*)"', replace_link, content)
    
    # Também corrigir src="/..."
    def replace_src(match):
        src = match.group(1)
        if src.startswith('/') and not src.startswith('//'):
            new_src = rel_prefix + src.lstrip('/')
            return f'src="{new_src}"'
        return match.group(0)

    new_content = re.sub(r'src="(/[^"]*)"', replace_src, new_content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    root_dir = "/home/ubuntu/comparapreco"
    fixed_count = 0
    for root, dirs, files in os.walk(root_dir):
        if ".git" in root or "scripts" in root:
            continue
        
        # Calcular profundidade relativa à raiz
        rel_path = os.path.relpath(root, root_dir)
        depth = 0 if rel_path == "." else len(rel_path.split(os.sep))
        
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                if fix_links_in_file(filepath, depth):
                    fixed_count += 1
                    print(f"Corrigido: {filepath} (profundidade {depth})")

    print(f"Total de arquivos corrigidos: {fixed_count}")

if __name__ == "__main__":
    main()
