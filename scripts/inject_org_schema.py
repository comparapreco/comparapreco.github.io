import os
import re
import json
from pathlib import Path

def inject_org_schema():
    root = Path('/home/ubuntu/comparapreco.github.io')
    index_file = root / 'index.html'
    
    if not index_file.exists(): return
    
    content = index_file.read_text(errors='replace')
    
    org_schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Compara Preço",
        "url": "https://comparapreco.github.io/",
        "logo": "https://comparapreco.github.io/assets/img/logo.png",
        "sameAs": [
            "https://twitter.com/comparapreco",
            "https://facebook.com/comparapreco"
        ],
        "description": "Especialistas em comparação de preços e análises de produtos no Brasil.",
        "founder": {
            "@type": "Person",
            "name": "Equipe Compara Preço"
        }
    }
    
    schema_json = json.dumps(org_schema, indent=2, ensure_ascii=False)
    schema_html = f'\n  <script type="application/ld+json">\n{schema_json}\n  </script>'
    
    if 'Organization' not in content:
        content = content.replace('</head>', schema_html + '\n</head>')
        index_file.write_text(content)
        print("Schema Organization injetado na Home.")

if __name__ == "__main__":
    inject_org_schema()
