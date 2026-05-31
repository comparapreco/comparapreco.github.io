import os
import json
from datetime import datetime
from generate_blog_posts import generate_long_content

def migrate():
    posts_dir = 'noticias/posts'
    offers_file = 'data/products/offers.json'
    
    if not os.path.exists(offers_file):
        print("Arquivo de ofertas não encontrado.")
        return

    with open(offers_file, 'r') as f:
        products = json.load(f)
    
    # Mapear produtos por ID para facilitar a busca
    prod_map = {p.get('id'): p for p in products}
    
    files = [f for f in os.listdir(posts_dir) if f.endswith('.html')]
    
    for filename in files:
        # Pular o post da missão e o que já foi gerado no novo formato
        if 'missao' in filename or 'analise-completa' in filename:
            continue
            
        path = os.path.join(posts_dir, filename)
        
        # Tentar identificar o produto pelo nome do arquivo ou conteúdo
        # Como os nomes antigos eram compara-ofertas-..., vamos pegar um produto aleatório 
        # ou os top produtos para preencher esses posts antigos com conteúdo de valor.
        
        target_product = random.choice(products)
        
        new_title = f"Análise Completa: Vale a Pena Comprar o {target_product.get('name')} em 2026?"
        article_body = generate_long_content(target_product)
        now = datetime.now()

        content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{new_title} | Compara Preço</title>
            <meta name="description" content="Análise aprofundada do {target_product.get('name')}. Descubra se vale a pena comprar com {target_product.get('custom_discount_pct')}% de desconto.">
            <link rel="stylesheet" href="../../assets/css/style.css">
        </head>
        <body>
            <header class="header"><div class="container"><a href="../../" class="logo">📊 Compara Preço</a></div></header>
            <main class="container" style="padding: 40px 20px; max-width: 900px; margin: 0 auto;">
                <article>
                    <header style="margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px;">
                        <h1>{new_title}</h1>
                        <p style="color: #666;">Publicado por Equipe Compara Preço em {now.strftime('%d/%m/%Y %H:%M')} | Leitura de 15 min</p>
                    </header>
                    <div class="content" style="line-height: 1.8; font-size: 16px; color: #333;">
                        {article_body}
                    </div>
                    <div style="margin-top: 40px; padding: 20px; background: #f9f9f9; border-radius: 10px; text-align: center;">
                        <h3>🔥 Gostou desta oferta?</h3>
                        <p>O {target_product.get('name')} está com estoque limitado!</p>
                        <a href="{target_product.get('custom_affiliate_url')}" class="btn" style="background: #00a83f; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">VER OFERTA NO MERCADO LIVRE</a>
                    </div>
                    <div style="margin-top: 40px;">
                        <a href="../../" class="btn">← Voltar para a Home</a>
                    </div>
                </article>
            </main>
            <footer class="footer" style="margin-top: 60px; padding: 40px 0; border-top: 1px solid #eee; text-align: center;">
                <p>© 2026 Compara Preço - Conteúdo Original e Protegido.</p>
            </footer>
        </body>
        </html>
        """
        
        with open(path, 'w') as f:
            f.write(content)
        print(f"Post migrado para formato longo: {filename}")

if __name__ == "__main__":
    import random
    migrate()
