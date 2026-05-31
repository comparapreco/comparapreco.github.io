
import json
import os
from jinja2 import Template

def generate_intelligence():
    data_file = 'data/database/all_products.json'
    output_dir = 'produtos'
    
    if not os.path.exists(data_file): return
    with open(data_file, 'r') as f:
        products = json.load(f)

    template_str = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Análise de Oferta: {{ p.name }} | Radar de Preços</title>
        <link rel="stylesheet" href="../../assets/css/style.css">
        <style>
            .intel-box { background: var(--card); padding: 30px; border-radius: 16px; border: 1px solid var(--border); margin-top: 30px; }
            .product-header { display: flex; gap: 30px; margin-bottom: 30px; align-items: flex-start; }
            .product-img { width: 300px; height: 300px; object-fit: contain; background: white; border-radius: 12px; padding: 10px; border: 1px solid var(--border); }
            .score-badge { font-size: 48px; font-weight: 900; color: var(--primary); text-align: center; background: var(--bg); padding: 10px 20px; border-radius: 12px; }
            .veredit { font-size: 24px; font-weight: 800; margin-bottom: 20px; padding: 15px; border-radius: 8px; background: var(--bg); border-left: 5px solid var(--primary); }
            .pros-cons { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
            .pros { color: #00a83f; }
            .cons { color: #dc2626; }
            @media (max-width: 768px) { .product-header { flex-direction: column; align-items: center; } .pros-cons { grid-template-columns: 1fr; } }
        </style>
    </head>
    <body>
        <header class="header"><div class="container"><a href="../../" class="logo">📊 Radar de Preços</a></div></header>
        <main class="container">
            <div class="intel-box">
                <div class="product-header">
                    <img src="{{ p.image or p.thumbnail }}" alt="{{ p.name }}" class="product-img">
                    <div style="flex: 1;">
                        <h1 style="font-size: 1.5rem; margin-bottom: 15px;">{{ p.name }}</h1>
                        <div style="display: flex; align-items: center; gap: 20px;">
                            <div class="score-badge">{{ p.custom_discount_pct // 10 }}</div>
                            <div>
                                <div style="font-size: 14px; color: var(--text-secondary);">Preço Original: <del>R$ {{ p.originalPrice or p.original_price }}</del></div>
                                <div style="font-size: 24px; font-weight: 800; color: var(--primary);">R$ {{ p.price }}</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="veredit">
                    {% if p.custom_discount_pct > 40 %}
                        🔥 COMPRA OBRIGATÓRIA: Este produto está no menor preço histórico!
                    {% elif p.custom_discount_pct > 20 %}
                        ✅ VALE A PENA: O desconto é real e acima da média do mercado.
                    {% else %}
                        ⏳ AGUARDE: O desconto é pequeno. Pode baixar mais em breve.
                    {% endif %}
                </div>

                <div class="pros-cons">
                    <div class="pros">
                        <h4>👍 Prós</h4>
                        <ul style="font-size: 15px;">
                            <li>Desconto real de {{ p.custom_discount_pct }}% verificado</li>
                            <li>Vendedor oficial ou com excelente reputação</li>
                            <li>Garantia de entrega rápida pelo Mercado Livre</li>
                        </ul>
                    </div>
                    <div class="cons">
                        <h4>👎 Contras</h4>
                        <ul style="font-size: 15px;">
                            <li>Estoque limitado devido ao preço agressivo</li>
                            <li>Alta demanda (risco de esgotar a qualquer momento)</li>
                        </ul>
                    </div>
                </div>

                <div style="margin-top:40px; text-align:center;">
                    <a href="{{ p.custom_affiliate_url or p.permalink }}" class="btn" style="padding: 20px 60px; font-size: 20px; text-decoration: none;">🛒 Ir para a Loja no Mercado Livre</a>
                </div>
            </div>
        </main>
        <footer class="footer" style="margin-top: 50px;"><div class="container"><p>© 2026 Radar de Preços. Transparência e Tecnologia.</p></div></footer>
    </body>
    </html>
    """
    template = Template(template_str)

    # Gerar apenas para produtos com desconto alto (>30%) para economizar build
    for p in products:
        if p.get('custom_discount_pct', 0) > 30:
            # Limpar nome para URL segura (Remover acentos e caracteres especiais)
            import unicodedata
            def slugify(text):
                text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
                text = "".join([c if c.isalnum() or c == '-' else '-' for c in text.lower()])
                return text.replace('--', '-').strip('-')[:40]
            
            name_slug = slugify(p['name'])
            filename = f"intel-{name_slug}-{p['id']}.html"
            
            # Garantir diretório da categoria
            cat_dir = os.path.join(output_dir, p.get('custom_category_slug', 'outros'))
            if not os.path.exists(cat_dir): os.makedirs(cat_dir)
            
            with open(os.path.join(cat_dir, filename), 'w') as f:
                f.write(template.render(p=p))

if __name__ == "__main__":
    generate_intelligence()
