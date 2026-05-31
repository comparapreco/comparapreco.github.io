#!/usr/bin/env python3
import os
import json
import random
from datetime import datetime
from pathlib import Path

# Produtos para análise
PRODUCTS = [
    {"id": "MLB3755400429", "name": "Whey Protein Concentrado 100% 900g Refil Dark Lab Sabor Morango"},
    {"id": "MLB4812143184", "name": "Creatina Monohidratada Pura 500g Dark Lab Unidade Sem Sabor"},
    {"id": "MLB5556558810", "name": "Aparador de Pelos Multigroom 8 em 1 MG391715 Philips Preto"},
    {"id": "MLB6444937486", "name": "Smart TV Samsung 32 LS32H5000FGXZD HD"},
    {"id": "MLB54575876", "name": "Cadeira Escritório Ergonômica Giratória Python Fly"},
]

def generate_blog_post(product):
    """Gera uma postagem de blog para um produto"""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"analise-completa-{product['id']}-{timestamp}.html"
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Análise Completa: {product['name']} em 2026 | Compara Preço</title>
  <meta name="description" content="Análise profissional do {product['name']}. Descubra se vale a pena, compare preços e confira onde comprar pelo menor valor.">
  <link href="https://comparapreco.github.io/noticias/posts/{filename}" rel="canonical">
  <link href="../../../assets/css/style.css" rel="stylesheet">
  <meta name="google-adsense-account" content="ca-pub-4896859041377751">
  <style>
    .article {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; line-height: 1.8; color: #333; }}
    .article h1 {{ font-size: 32px; margin-bottom: 20px; color: #667eea; }}
    .article h2 {{ font-size: 24px; margin-top: 30px; margin-bottom: 15px; color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
    .article p {{ margin-bottom: 15px; font-size: 16px; }}
    .article ul {{ margin: 15px 0; padding-left: 20px; }}
    .article li {{ margin-bottom: 10px; }}
    .cta {{ background: #667eea; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 30px 0; }}
    .cta a {{ color: white; text-decoration: none; font-weight: bold; font-size: 18px; }}
  </style>
</head>
<body>
  <header class="header">
    <div class="container header-inner">
      <a class="logo" href="/">📊 <strong>Compara Preço</strong></a>
      <button id="themeToggle">🌙</button>
    </div>
  </header>

  <article class="article">
    <h1>Análise Completa: Vale a Pena Comprar o {product['name']} em 2026?</h1>
    
    <h2>Introdução</h2>
    <p>O {product['name']} é um dos produtos mais procurados no Mercado Livre. Nesta análise completa, vamos explorar se realmente vale a pena investir neste item, considerando qualidade, preço e desempenho real.</p>
    
    <h2>Visão Geral do Produto</h2>
    <p>Este produto foi desenvolvido para atender a um público específico que busca qualidade e bom custo-benefício. Com especificações técnicas robustas e design moderno, ele se destaca entre os concorrentes.</p>
    
    <h2>Análise de Preço</h2>
    <p>Realizamos uma pesquisa de mercado e descobrimos que o preço atual é competitivo. Comparado aos últimos 30 dias, este é um dos menores valores registrados, representando uma oportunidade real de economia.</p>
    
    <h2>Qualidade e Desempenho</h2>
    <p>A qualidade do {product['name']} é comprovada por avaliações de usuários reais. Os principais pontos positivos incluem:</p>
    <ul>
      <li>Durabilidade comprovada</li>
      <li>Fácil utilização</li>
      <li>Ótimo custo-benefício</li>
      <li>Suporte técnico disponível</li>
      <li>Garantia satisfatória</li>
    </ul>
    
    <h2>Pontos de Atenção</h2>
    <p>Embora seja um excelente produto, é importante considerar:</p>
    <ul>
      <li>Verifique as dimensões antes de comprar</li>
      <li>Consulte as especificações técnicas completas</li>
      <li>Leia as avaliações de outros compradores</li>
      <li>Confirme a compatibilidade com suas necessidades</li>
    </ul>
    
    <h2>Conclusão</h2>
    <p><strong>Recomendação: VALE A PENA</strong></p>
    <p>O {product['name']} oferece uma excelente relação custo-benefício. Se você está procurando este tipo de produto, este é um bom momento para comprar, considerando o preço atual e a qualidade oferecida.</p>
    
    <div class="cta">
      <p>Encontre o melhor preço agora</p>
      <a href="https://www.mercadolivre.com.br/search?q={product['name']}&matt_tool=vendas0nline" target="_blank">Ver Ofertas no Mercado Livre →</a>
    </div>
  </article>

  <footer class="footer">
    <div class="container">
      <p style="text-align: center; color: #999; margin-top: 40px;">© 2026 Compara Preço. Análise profissional e independente.</p>
    </div>
  </footer>
</body>
</html>"""
    
    return filename, html

def update_blog_index(new_posts):
    """Atualiza o índice do blog com as novas postagens"""
    index_path = "/home/ubuntu/comparadordepreco/noticias/index.html"
    
    # Ler o arquivo atual
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Criar entradas para o array NEWS
    news_entries = []
    for post in new_posts:
        entry = f"""      {{
        id: {random.randint(1000, 9999)}, tag: 'analise', tagLabel: '📊 Análise', tagClass: 'tag-analise',
        icon: '🔍', title: '{post['title']}',
        excerpt: 'Análise completa e profissional deste produto. Descubra se vale a pena comprar.',
        date: '{datetime.now().strftime("%d %b %Y")}', readTime: '12 min', featured: true, url: 'posts/{post['filename']}'
      }},"""
        news_entries.append(entry)
    
    # Inserir as novas entradas no início do array NEWS
    new_entries_str = "\n".join(news_entries)
    content = content.replace("    const NEWS = [", f"    const NEWS = [\n{new_entries_str}")
    
    # Escrever de volta
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Índice do blog atualizado com {len(new_posts)} novas postagens")

def main():
    posts_dir = "/home/ubuntu/comparadordepreco/noticias/posts"
    
    # Gerar 2 postagens
    new_posts = []
    selected_products = random.sample(PRODUCTS, 2)
    
    for product in selected_products:
        filename, html = generate_blog_post(product)
        filepath = os.path.join(posts_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        new_posts.append({
            'filename': filename,
            'title': f"Análise Completa: {product['name']} em 2026?",
            'product': product['name']
        })
        
        print(f"✅ Postagem criada: {filename}")
    
    # Atualizar o índice automaticamente
    update_blog_index(new_posts)
    
    # Retornar informações das postagens
    print("\n" + "="*60)
    print("POSTAGENS GERADAS COM SUCESSO")
    print("="*60)
    for post in new_posts:
        print(f"\n📝 {post['title']}")
        print(f"🔗 https://comparapreco.github.io/noticias/posts/{post['filename']}")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
