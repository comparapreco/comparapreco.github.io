import os
import re
from pathlib import Path

def inject_social_meta():
    root = Path('/home/ubuntu/comparapreco.github.io')
    
    for html_file in root.glob('**/*.html'):
        if 'node_modules' in str(html_file): continue
        content = html_file.read_text(errors='replace')
        
        # Extrair dados para os metadados
        title_match = re.search(r'<title>(.*?)</title>', content)
        title = title_match.group(1) if title_match else "Compara Preço"
        
        desc_match = re.search(r'<meta name="description" content="(.*?)">', content)
        desc = desc_match.group(1) if desc_match else "As melhores ofertas e comparativos de 2026."
        
        img_match = re.search(r'<img[^>]+src="([^"]+)"', content)
        image = img_match.group(1) if img_match else "https://comparapreco.github.io/assets/img/og-default.jpg"
        if not image.startswith('http'):
            image = "https://comparapreco.github.io/" + image.replace('../', '').replace('./', '')

        social_meta = f"""
    <!-- Social Meta Tags -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:image" content="{image}">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="{image}">"""

        if 'og:title' not in content:
            content = content.replace('</head>', social_meta + '\n</head>')
            html_file.write_text(content)

if __name__ == "__main__":
    inject_social_meta()
