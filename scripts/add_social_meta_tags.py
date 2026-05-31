#!/usr/bin/env python3
"""
Adiciona tags Open Graph, Twitter Cards e favicon ao index.html
"""

import re

def add_social_meta_tags():
    file_path = 'index.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Tags Open Graph e Twitter Card para adicionar
    og_twitter_tags = '''  <meta property="og:type" content="website">
  <meta property="og:title" content="Compara Preço — As Melhores Ofertas do Mercado Livre Hoje">
  <meta property="og:description" content="Economize com as melhores ofertas curadas do Mercado Livre. Descubra produtos com desconto de até 70% em eletrônicos, casa, beleza e muito mais.">
  <meta property="og:url" content="https://comparapreco.github.io/">
  <meta property="og:image" content="https://comparapreco.github.io/assets/images/og-image.png">
  <meta property="og:site_name" content="Compara Preço">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Compara Preço — As Melhores Ofertas do Mercado Livre Hoje">
  <meta name="twitter:description" content="Economize com as melhores ofertas curadas do Mercado Livre. Descubra produtos com desconto de até 70%.">
  <meta name="twitter:image" content="https://comparapreco.github.io/assets/images/og-image.png">
  <link rel="icon" type="image/png" href="./assets/images/favicon.png">
  <link rel="apple-touch-icon" href="./assets/images/apple-touch-icon.png">'''
    
    # Encontrar o local para inserir (após meta charset)
    insert_position = html.find('</head>')
    
    if insert_position != -1:
        # Verificar se as tags já existem
        if 'og:title' not in html:
            html = html[:insert_position] + og_twitter_tags + '\n  ' + html[insert_position:]
            print("✅ Tags Open Graph e Twitter Card adicionadas com sucesso!")
        else:
            print("⚠️  Tags Open Graph e Twitter Card já existem.")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    add_social_meta_tags()
