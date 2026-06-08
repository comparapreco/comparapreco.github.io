import os
import re
import json
from pathlib import Path

def inject_breadcrumb():
    root = Path('/home/ubuntu/comparapreco.github.io')
    base_url = "https://comparapreco.github.io/"
    
    for html_file in root.glob('**/*.html'):
        if 'node_modules' in str(html_file) or html_file.name == 'index.html': continue
        content = html_file.read_text(errors='replace')
        
        # 1. Detectar estrutura pelo caminho do arquivo
        rel_path = html_file.relative_to(root)
        parts = rel_path.parts
        
        items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": base_url}]
        
        current_url = base_url
        for i, part in enumerate(parts):
            name = part.replace('.html', '').replace('-', ' ').title()
            current_url += part
            if i == len(parts) - 1:
                items.append({"@type": "ListItem", "position": i + 2, "name": name})
            else:
                items.append({"@type": "ListItem", "position": i + 2, "name": name, "item": current_url})
                current_url += "/"

        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }
        
        schema_json = json.dumps(breadcrumb_schema, indent=2, ensure_ascii=False)
        schema_html = f'\n  <script type="application/ld+json">\n{schema_json}\n  </script>'
        
        if 'BreadcrumbList' not in content:
            content = content.replace('</head>', schema_html + '\n</head>')
            html_file.write_text(content)

if __name__ == "__main__":
    inject_breadcrumb()
