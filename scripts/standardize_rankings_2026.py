import os
import re
from pathlib import Path

def standardize():
    root = Path('/home/ubuntu/comparapreco.github.io')
    rankings_dir = root / 'melhores-2026'
    
    # Template de Head otimizado
    head_template = """<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Ranking Atualizado 2026 | Compara Preço</title>
  <meta name="description" content="Descubra os {category_name} de 2026 com melhor custo-benefício. Ranking validado com preços, análises e ofertas reais atualizadas.">
  <link rel="canonical" href="https://comparapreco.github.io/melhores-2026/{filename}">
  <link rel="stylesheet" href="../assets/css/style.css">
  <style>
    .hero-ranking {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; padding: 60px 0 40px; text-align: center; border-bottom: 4px solid var(--primary); margin-bottom: 40px; }}
    .hero-ranking h1 {{ font-size: 2.5rem; font-weight: 900; margin-bottom: 15px; }}
    .hero-ranking p {{ font-size: 1.1rem; opacity: 0.9; max-width: 700px; margin: 0 auto; }}
    .ranking-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 25px; margin-bottom: 60px; }}
    .rank-card {{ background: var(--card); border-radius: 20px; border: 1px solid var(--border); padding: 20px; position: relative; transition: all 0.3s ease; display: flex; flex-direction: column; box-shadow: var(--shadow); }}
    .rank-card:hover {{ transform: translateY(-8px); box-shadow: var(--shadow-lg); border-color: var(--primary-light); }}
    .rank-badge {{ position: absolute; top: -15px; left: 20px; background: var(--primary); color: white; width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1.2rem; box-shadow: 0 4px 10px rgba(0, 200, 83, 0.4); z-index: 10; }}
    .rank-card-img {{ width: 100%; height: 200px; object-fit: contain; margin-bottom: 20px; border-radius: 12px; background: #fff; }}
    .rank-card-title {{ font-size: 1.1rem; font-weight: 800; margin-bottom: 12px; line-height: 1.4; flex-grow: 1; }}
    .rank-card-title a {{ color: var(--text); text-decoration: none; transition: color 0.2s; }}
    .rank-card-title a:hover {{ color: var(--primary); }}
    .rank-card-price {{ margin-bottom: 15px; }}
    .price-now {{ font-size: 1.5rem; font-weight: 900; color: var(--primary); }}
    .price-off {{ font-size: 0.9rem; color: var(--success); background: #dcfce7; padding: 2px 8px; border-radius: 6px; font-weight: 700; margin-left: 8px; }}
    .rank-card-meta {{ font-size: 0.85rem; color: var(--text-muted); margin-bottom: 20px; border-top: 1px solid #f1f5f9; padding-top: 12px; }}
    .btn-rank {{ display: block; text-align: center; background: var(--secondary); color: white; text-decoration: none; padding: 12px; border-radius: 12px; font-weight: 700; transition: all 0.2s; }}
    .btn-rank:hover {{ background: var(--primary); transform: scale(1.02); }}
  </style>
</head>"""

    html_files = list(rankings_dir.glob('*.html'))
    
    for file_path in html_files:
        if file_path.name in ['index.html', 'melhores-eletrodomesticos-2026.html']: continue
        
        content = file_path.read_text(errors='replace')
        
        # Extrair o título original
        title_match = re.search(r'<title>(.*?)</title>', content)
        original_title = title_match.group(1) if title_match else "Ranking 2026"
        
        # Determinar nome da categoria
        category_name = original_title.split(' de ')[0].replace('Melhores ', '')
        
        # Construir novo Head
        new_head = head_template.format(
            title=original_title,
            category_name=category_name.lower(),
            filename=file_path.name
        )
        
        # Substituir Head
        content = re.sub(r'<head>.*?</head>', new_head, content, flags=re.DOTALL)
        
        # Atualizar Header para o novo padrao
        header_html = """<header class="header">
    <div class="container">
      <a href="../" class="logo">📊 Compara Preço</a>
      <nav class="nav-links">
        <a href="../noticias/">Notícias</a>
        <a href="../melhores-2026/">Rankings 2026</a>
      </nav>
    </div>
  </header>"""
        content = re.sub(r'<header.*?</header>', header_html, content, flags=re.DOTALL)
        
        # Envelopar main com container se nao tiver
        if '<main class="container">' not in content:
             content = content.replace('<body>', '<body>\n  ' + header_html)
             # Tentar achar o h1 para colocar o main
             content = content.replace('<h1', '<main class="container">\n    <h1')
             content = content.replace('</body>', '  </main>\n</body>')

        # Converter rank-item para rank-card (simplificado)
        content = content.replace('class="rank-item"', 'class="rank-card"')
        content = content.replace('class="rank-number"', 'class="rank-badge"')
        content = content.replace('class="rank-img"', 'class="rank-card-img"')
        content = content.replace('class="rank-info"', '')
        content = content.replace('class="price-tag"', 'class="rank-card-price"')
        content = content.replace('class="btn"', 'class="btn-rank"')
        
        file_path.write_text(content)
        print(f"Padronizado: {file_path.name}")

if __name__ == "__main__":
    standardize()
 
