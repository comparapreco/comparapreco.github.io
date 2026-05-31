#!/usr/bin/env python3
"""
Gera landing pages automáticas de marcas em /melhores-ofertas/{marca}/
"""
import json
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PRODUCTS_FILE = BASE_DIR / 'data' / 'products' / 'offers.json'
OUTPUT_DIR = BASE_DIR / 'melhores-ofertas'

BRANDS = {
    'samsung':  {'name': 'Samsung',  'icon': '📱', 'color': '#1428a0', 'desc': 'Smartphones, TVs, eletrodomésticos e muito mais da Samsung com os melhores preços.'},
    'lg':       {'name': 'LG',       'icon': '📺', 'color': '#a50034', 'desc': 'TVs, eletrodomésticos e eletrônicos LG com desconto garantido.'},
    'lenovo':   {'name': 'Lenovo',   'icon': '💻', 'color': '#e2231a', 'desc': 'Notebooks, tablets e acessórios Lenovo com os melhores preços do mercado.'},
    'apple':    {'name': 'Apple',    'icon': '🍎', 'color': '#555555', 'desc': 'iPhone, MacBook, iPad e AirPods Apple com desconto real.'},
    'xiaomi':   {'name': 'Xiaomi',   'icon': '📱', 'color': '#ff6900', 'desc': 'Smartphones, smartwatches e eletrônicos Xiaomi com ótimo custo-benefício.'},
    'sony':     {'name': 'Sony',     'icon': '🎮', 'color': '#003087', 'desc': 'PlayStation, TVs, fones e câmeras Sony com os melhores preços.'},
    'philips':  {'name': 'Philips',  'icon': '💡', 'color': '#0b5ed7', 'desc': 'Eletrodomésticos, iluminação e eletrônicos Philips com desconto.'},
    'multilaser':{'name':'Multilaser','icon':'🖥️', 'color': '#e63946', 'desc': 'Notebooks, tablets e eletrônicos Multilaser com preço acessível.'},
}

TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Melhores Ofertas {name} — Desconto Real | Compara Preço</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="https://comparapreco.github.io/melhores-ofertas/{slug}/">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://comparapreco.github.io/melhores-ofertas/{slug}/">
  <meta property="og:title" content="Melhores Ofertas {name} | Compara Preço">
  <meta property="og:description" content="{desc}">
  <link rel="stylesheet" href="../../assets/css/style.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
  <meta name="google-adsense-account" content="ca-pub-4896859041377751">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "Melhores Ofertas {name}",
    "description": "{desc}",
    "url": "https://comparapreco.github.io/melhores-ofertas/{slug}/",
    "breadcrumb": {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Início", "item": "https://comparapreco.github.io/"}},
        {{"@type": "ListItem", "position": 2, "name": "Melhores Ofertas", "item": "https://comparapreco.github.io/melhores-ofertas/"}},
        {{"@type": "ListItem", "position": 3, "name": "{name}"}}
      ]
    }}
  }}
  </script>
  <style>
    .brand-hero {{
      background: linear-gradient(135deg, {color} 0%, {color}cc 100%);
      color: white;
      padding: 50px 0 40px;
      margin-bottom: 40px;
    }}
    .brand-hero h1 {{ font-size: 2rem; margin-bottom: 10px; }}
    .brand-hero p {{ opacity: 0.9; font-size: 1.05rem; max-width: 600px; }}
    .breadcrumb {{ font-size: 13px; opacity: 0.8; margin-bottom: 15px; }}
    .breadcrumb a {{ color: white; text-decoration: none; }}
    .brand-icon {{ font-size: 3rem; margin-bottom: 10px; }}
    .brand-stats {{
      display: flex; gap: 20px; flex-wrap: wrap; margin-top: 20px;
    }}
    .brand-stat {{
      background: rgba(255,255,255,0.2);
      border-radius: 10px;
      padding: 10px 18px;
      font-size: 14px;
      font-weight: 700;
    }}
    .section-title {{ font-size: 1.3rem; font-weight: 800; margin-bottom: 20px; }}
    .no-products {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 60px 20px;
      text-align: center;
      color: var(--text-light);
      margin-bottom: 40px;
    }}
    .no-products h3 {{ font-size: 1.2rem; margin-bottom: 10px; }}
    .related-brands {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 12px;
      margin-bottom: 40px;
    }}
    .brand-link {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      text-align: center;
      text-decoration: none;
      color: var(--text);
      font-weight: 700;
      font-size: 14px;
      transition: all 0.2s;
    }}
    .brand-link:hover {{ border-color: var(--primary); color: var(--primary); }}
    .brand-link .bi {{ font-size: 1.5rem; display: block; margin-bottom: 6px; }}
    .faq-section {{ margin-bottom: 40px; }}
    .faq-item {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 12px; }}
    .faq-q {{ font-weight: 700; margin-bottom: 8px; }}
    .faq-a {{ font-size: 14px; color: var(--text-light); line-height: 1.6; }}
  </style>
</head>
<body>
  <header class="header">
    <div class="container header-inner">
      <a href="../../" class="logo">📊 <strong>Compara Preço</strong></a>
      <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Buscar ofertas...">
      </div>
      <button id="themeToggle">🌙</button>
    </div>
  </header>

  <section class="brand-hero">
    <div class="container">
      <div class="breadcrumb"><a href="../../">Início</a> › <a href="../">Melhores Ofertas</a> › {name}</div>
      <div class="brand-icon">{icon}</div>
      <h1>Melhores Ofertas {name}</h1>
      <p>{desc}</p>
      <div class="brand-stats" id="brandStats">
        <div class="brand-stat" id="bsTotalProds">Carregando...</div>
        <div class="brand-stat" id="bsAvgDisc">Desc. Médio: -</div>
        <div class="brand-stat" id="bsMaxDisc">Maior Desc.: -</div>
      </div>
    </div>
  </section>

  <main class="container">

    <h2 class="section-title">{icon} Ofertas {name} em Destaque</h2>
    <div class="products-grid" id="brandProducts">
      <div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-light);">Carregando ofertas {name}...</div>
    </div>

    <!-- Outras marcas -->
    <h2 class="section-title">🏷️ Outras Marcas em Destaque</h2>
    <div class="related-brands">
      <a href="../samsung/" class="brand-link"><span class="bi">📱</span>Samsung</a>
      <a href="../lg/" class="brand-link"><span class="bi">📺</span>LG</a>
      <a href="../lenovo/" class="brand-link"><span class="bi">💻</span>Lenovo</a>
      <a href="../apple/" class="brand-link"><span class="bi">🍎</span>Apple</a>
      <a href="../xiaomi/" class="brand-link"><span class="bi">📱</span>Xiaomi</a>
      <a href="../sony/" class="brand-link"><span class="bi">🎮</span>Sony</a>
    </div>

    <!-- FAQ para SEO -->
    <div class="faq-section">
      <h2 class="section-title">❓ Perguntas Frequentes sobre {name}</h2>
      <div class="faq-item">
        <div class="faq-q">Onde encontrar as melhores ofertas {name}?</div>
        <div class="faq-a">O Compara Preço monitora automaticamente os produtos {name} no Mercado Livre e outros grandes varejistas, exibindo apenas as ofertas com desconto real em relação ao preço histórico.</div>
      </div>
      <div class="faq-item">
        <div class="faq-q">Como saber se o desconto {name} é real?</div>
        <div class="faq-a">Nosso sistema compara o preço atual com o histórico de 90 dias de cada produto. Apenas produtos com desconto genuíno em relação ao preço médio histórico são exibidos nesta página.</div>
      </div>
      <div class="faq-item">
        <div class="faq-q">Com que frequência as ofertas {name} são atualizadas?</div>
        <div class="faq-a">As ofertas são atualizadas automaticamente várias vezes ao dia via API oficial do Mercado Livre. Você sempre verá os preços mais recentes disponíveis.</div>
      </div>
    </div>

  </main>

  <footer class="footer">
    <div class="container">
      <p>© 2026 Compara Preço. Atualizado via API oficial do Mercado Livre.</p>
      <div class="footer-links">
        <a href="../../sobre/">Sobre</a>
        <a href="../../contato/">Contato</a>
        <a href="../../privacidade/">Privacidade</a>
        <a href="../../indice-compara/">Índice Compara Preço</a>
        <a href="../../tendencias/">Tendências</a>
      </div>
    </div>
  </footer>

  <script>
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    document.getElementById('themeToggle').addEventListener('click', () => {{
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      document.getElementById('themeToggle').textContent = next === 'dark' ? '☀️' : '🌙';
    }});
    if (savedTheme === 'dark') document.getElementById('themeToggle').textContent = '☀️';
    document.getElementById('searchInput').addEventListener('keydown', e => {{
      if (e.key === 'Enter') {{ const q = e.target.value.trim(); if (q) window.location.href = `../../?q=${{encodeURIComponent(q)}}`; }}
    }});

    const BRAND_SLUG = '{slug}';
    const BRAND_NAME = '{name}';

    fetch('../../data/products/offers.json').then(r=>r.json()).then(products => {{
      // Filtra por marca no título
      const brandProducts = products.filter(p => {{
        const title = (p.title || p.name || '').toLowerCase();
        return title.includes(BRAND_SLUG.toLowerCase()) || title.includes(BRAND_NAME.toLowerCase());
      }});

      const allToShow = brandProducts.length > 0 ? brandProducts : products.slice(0, 8);

      if (brandProducts.length > 0) {{
        const discs = brandProducts.map(p => p.custom_discount_pct || 0);
        document.getElementById('bsTotalProds').textContent = `${{brandProducts.length}} produtos`;
        document.getElementById('bsAvgDisc').textContent = `Desc. Médio: ${{Math.round(discs.reduce((a,b)=>a+b,0)/discs.length)}}%`;
        document.getElementById('bsMaxDisc').textContent = `Maior Desc.: ${{Math.max(...discs)}}%`;
      }} else {{
        document.getElementById('bsTotalProds').textContent = 'Em breve';
        document.getElementById('bsAvgDisc').textContent = 'Monitorando...';
        document.getElementById('bsMaxDisc').textContent = 'Aguarde';
      }}

      const sorted = [...allToShow].sort((a,b) => (b.custom_discount_pct||0) - (a.custom_discount_pct||0));

      if (brandProducts.length === 0) {{
        document.getElementById('brandProducts').innerHTML = `
          <div class="no-products" style="grid-column:1/-1;">
            <h3>🔍 Monitorando produtos {name}...</h3>
            <p>Ainda não temos ofertas específicas de {name} no momento. Veja abaixo as melhores ofertas gerais enquanto isso.</p>
          </div>
          ${{sorted.map(p => renderCard(p)).join('')}}
        `;
      }} else {{
        document.getElementById('brandProducts').innerHTML = sorted.map(p => renderCard(p)).join('');
      }}
    }}).catch(err => console.error(err));

    function renderCard(p) {{
      const url = p.custom_affiliate_url || p.permalink || '#';
      const disc = p.custom_discount_pct || 0;
      const price = parseFloat(p.price||0).toLocaleString('pt-BR',{{minimumFractionDigits:2}});
      const orig = parseFloat(p.originalPrice||p.original_price||p.price||0).toLocaleString('pt-BR',{{minimumFractionDigits:2}});
      return `
        <div class="product-card">
          <a href="${{url}}" target="_blank" rel="noopener sponsored">
            <img src="${{p.image||p.thumbnail}}" alt="${{p.title}}" loading="lazy" onerror="this.src='../../assets/img/placeholder.png'">
            ${{disc>0?`<span class="badge-discount">-${{disc}}%</span>`:''}}
            <div class="product-info">
              <h3 class="product-name">${{(p.title||p.name||'').substring(0,70)}}</h3>
              <div class="product-price">
                ${{orig!==price?`<span class="price-original">R$ ${{orig}}</span>`:''}}
                <span class="price-current">R$ ${{price}}</span>
              </div>
              <a href="${{url}}" target="_blank" rel="noopener sponsored" class="btn-buy">Ver Oferta →</a>
            </div>
          </a>
        </div>
      `;
    }}
  </script>
</body>
</html>
'''

def build_brand_page(slug, brand):
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    html = TEMPLATE.format(
        slug=slug,
        name=brand['name'],
        icon=brand['icon'],
        color=brand['color'],
        desc=brand['desc']
    )
    (out_dir / 'index.html').write_text(html, encoding='utf-8')
    print(f"  ✅ /melhores-ofertas/{slug}/")

def build_hub():
    """Gera página hub /melhores-ofertas/index.html"""
    cards = '\n'.join([
        f'''      <a href="{slug}/" class="brand-hub-card">
        <div class="brand-hub-icon">{b['icon']}</div>
        <div class="brand-hub-name">{b['name']}</div>
        <div class="brand-hub-desc">{b['desc'][:60]}...</div>
      </a>'''
        for slug, b in BRANDS.items()
    ])

    hub = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Melhores Ofertas por Marca — Samsung, LG, Lenovo e mais | Compara Preço</title>
  <meta name="description" content="Encontre as melhores ofertas por marca: Samsung, LG, Lenovo, Apple, Xiaomi, Sony e muito mais. Descontos reais verificados pelo Compara Preço.">
  <link rel="canonical" href="https://comparapreco.github.io/melhores-ofertas/">
  <link rel="stylesheet" href="../assets/css/style.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
  <meta name="google-adsense-account" content="ca-pub-4896859041377751">
  <style>
    .page-hero {{ background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); color: white; padding: 50px 0 40px; margin-bottom: 40px; }}
    .page-hero h1 {{ font-size: 2rem; margin-bottom: 10px; }}
    .breadcrumb {{ font-size: 13px; opacity: 0.8; margin-bottom: 15px; }}
    .breadcrumb a {{ color: white; text-decoration: none; }}
    .brands-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; margin-bottom: 40px; }}
    .brand-hub-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 24px; text-decoration: none; color: inherit; display: block; transition: transform 0.2s, box-shadow 0.2s; }}
    .brand-hub-card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.1); border-color: var(--primary); }}
    .brand-hub-icon {{ font-size: 2.5rem; margin-bottom: 10px; }}
    .brand-hub-name {{ font-size: 1.2rem; font-weight: 800; margin-bottom: 6px; }}
    .brand-hub-desc {{ font-size: 13px; color: var(--text-light); line-height: 1.5; }}
    .section-title {{ font-size: 1.3rem; font-weight: 800; margin-bottom: 20px; }}
  </style>
</head>
<body>
  <header class="header">
    <div class="container header-inner">
      <a href="../" class="logo">📊 <strong>Compara Preço</strong></a>
      <div class="search-bar"><input type="text" id="searchInput" placeholder="Buscar ofertas..."></div>
      <button id="themeToggle">🌙</button>
    </div>
  </header>
  <section class="page-hero">
    <div class="container">
      <div class="breadcrumb"><a href="../">Início</a> › Melhores Ofertas por Marca</div>
      <h1>🏷️ Melhores Ofertas por Marca</h1>
      <p>Encontre as melhores promoções organizadas por fabricante. Descontos reais verificados pelo Compara Preço.</p>
    </div>
  </section>
  <main class="container">
    <h2 class="section-title">Escolha uma Marca</h2>
    <div class="brands-grid">
{cards}
    </div>
  </main>
  <footer class="footer">
    <div class="container">
      <p>© 2026 Compara Preço.</p>
      <div class="footer-links">
        <a href="../sobre/">Sobre</a>
        <a href="../contato/">Contato</a>
        <a href="../indice-compara/">Índice Compara Preço</a>
        <a href="../tendencias/">Tendências</a>
      </div>
    </div>
  </footer>
  <script>
    const t = localStorage.getItem('theme')||'light';
    document.documentElement.setAttribute('data-theme', t);
    document.getElementById('themeToggle').addEventListener('click', () => {{
      const c = document.documentElement.getAttribute('data-theme');
      const n = c==='dark'?'light':'dark';
      document.documentElement.setAttribute('data-theme', n);
      localStorage.setItem('theme', n);
      document.getElementById('themeToggle').textContent = n==='dark'?'☀️':'🌙';
    }});
    if (t==='dark') document.getElementById('themeToggle').textContent='☀️';
    document.getElementById('searchInput').addEventListener('keydown', e => {{
      if (e.key==='Enter') {{ const q=e.target.value.trim(); if(q) window.location.href=`../?q=${{encodeURIComponent(q)}}`; }}
    }});
  </script>
</body>
</html>'''
    (OUTPUT_DIR / 'index.html').write_text(hub, encoding='utf-8')
    print("  ✅ /melhores-ofertas/")

if __name__ == '__main__':
    print("Gerando landing pages de marcas...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    build_hub()
    for slug, brand in BRANDS.items():
        build_brand_page(slug, brand)
    print(f"\n✅ {len(BRANDS) + 1} páginas geradas!")
