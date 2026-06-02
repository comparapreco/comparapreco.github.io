#!/usr/bin/env python3
"""
Gerador de Páginas Melhorado - com Schema Markup, Open Graph, Alt Tags e Canonical
Compatível com Google AdSense
"""
import os
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

BASE_URL = "https://comparapreco.github.io"
ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now().strftime("%Y-%m-%d")


def sanitize_filename(text: str) -> str:
    """Converte texto em slug válido para URL."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def generate_product_schema(product: dict, url: str) -> str:
    """Gera Schema Markup para produto."""
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.get("name", "Produto"),
        "description": product.get("description", ""),
        "image": product.get("image", ""),
        "url": url,
        "offers": {
            "@type": "Offer",
            "price": str(product.get("current_price", 0)).replace("R$ ", ""),
            "priceCurrency": "BRL",
            "availability": "https://schema.org/InStock",
            "url": product.get("ml_link", "")
        }
    }
    if product.get("rating"):
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": product.get("rating", 0),
            "ratingCount": product.get("review_count", 0)
        }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def generate_article_schema(article: dict, url: str) -> str:
    """Gera Schema Markup para artigo."""
    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": article.get("title", ""),
        "description": article.get("description", ""),
        "image": article.get("image", ""),
        "datePublished": article.get("date", NOW),
        "dateModified": NOW,
        "author": {
            "@type": "Organization",
            "name": "Compara Preço",
            "url": BASE_URL
        },
        "publisher": {
            "@type": "Organization",
            "name": "Compara Preço",
            "logo": {
                "@type": "ImageObject",
                "url": f"{BASE_URL}/assets/logo.png",
                "width": 250,
                "height": 60
            }
        }
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def generate_organization_schema() -> str:
    """Gera Schema Markup para organização."""
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Compara Preço",
        "url": BASE_URL,
        "logo": f"{BASE_URL}/assets/logo.png",
        "description": "As melhores ofertas do Mercado Livre com atualização automática",
        "sameAs": [
            "https://www.instagram.com/comparapreco",
            "https://www.facebook.com/comparapreco"
        ],
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "Customer Service",
            "email": "contato@comparapreco.github.io"
        }
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def generate_product_page(product: dict, category: str) -> tuple:
    """Gera página HTML de produto com todas as melhorias."""
    
    # URLs e slugs
    product_slug = sanitize_filename(product.get("name", "produto"))
    page_url = f"{BASE_URL}/ofertas/{category}/{product_slug}.html"
    canonical_url = page_url
    
    # Schema Markup
    product_schema = generate_product_schema(product, page_url)
    org_schema = generate_organization_schema()
    
    # Descrição para meta tags
    description = product.get("description", "")[:160]
    title = f"{product.get('name', 'Produto')} - Compara Preço"
    
    # Imagem para OG
    image = product.get("image", f"{BASE_URL}/assets/og-default.png")
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{product.get('name', '')}, ofertas, mercado livre, compras">
    
    <!-- Canonical Tag -->
    <link rel="canonical" href="{canonical_url}">
    
    <!-- Open Graph Tags -->
    <meta property="og:type" content="product">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{image}">
    <meta property="og:url" content="{page_url}">
    <meta property="og:site_name" content="Compara Preço">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{image}">
    
    <!-- Schema Markup -->
    <script type="application/ld+json">
    {product_schema}
    </script>
    <script type="application/ld+json">
    {org_schema}
    </script>
    
    <!-- Google AdSense -->
    <meta name="google-adsense-account" content="ca-pub-4896859041377751">
    
    <link rel="stylesheet" href="../../assets/css/style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <a href="/" class="logo">📊 Compara Preço</a>
            <nav>
                <a href="/noticias/">Blog</a>
                <a href="/sobre/">Sobre</a>
                <a href="/contato/">Contato</a>
            </nav>
        </div>
    </header>
    
    <main class="container" style="padding: 40px 20px; max-width: 900px; margin: 0 auto;">
        <!-- Breadcrumb -->
        <nav aria-label="breadcrumb" style="margin-bottom: 20px;">
            <a href="/">Home</a> / 
            <a href="/ofertas/">Ofertas</a> / 
            <a href="/categorias/{category}/">{category.title()}</a> / 
            <span>{product.get('name', 'Produto')}</span>
        </nav>
        
        <article>
            <header style="margin-bottom: 30px; border-bottom: 2px solid #0f766e; padding-bottom: 20px;">
                <div style="color: #0f766e; font-weight: bold; font-size: 12px; margin-bottom: 10px; text-transform: uppercase;">
                    {category.upper()} • OFERTA DO DIA
                </div>
                <h1 style="margin: 0; font-size: 28px; color: #1a1a1a;">{product.get('name', 'Produto')}</h1>
                <p style="color: #666; margin-top: 10px; font-size: 14px;">
                    Atualizado em {NOW} • Compara Preço
                </p>
            </header>
            
            <!-- Produto Principal -->
            <div style="background: #f9f9f9; padding: 30px; border-radius: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 40px; align-items: center;">
                <div>
                    <img src="{image}" 
                         alt="{product.get('name', 'Produto')} - {product.get('current_price', 'Preço')}"
                         style="width: 100%; max-width: 300px; height: auto; border-radius: 8px; background: white; padding: 10px;">
                </div>
                <div>
                    <div style="font-size: 32px; font-weight: 800; color: #d32f2f; margin-bottom: 10px;">
                        {product.get('current_price', 'Consulte')}
                    </div>
                    <div style="color: #388e3c; font-weight: bold; font-size: 18px; margin-bottom: 20px;">
                        {product.get('discount', '0%')} OFF
                    </div>
                    <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #ffc107;">
                        <strong>⚡ Oferta por tempo limitado!</strong> Preço pode variar a qualquer momento.
                    </div>
                    <a href="{product.get('ml_link', '#')}" 
                       class="btn" 
                       style="display: inline-block; background: #0f766e; color: white; padding: 15px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                        Ver Oferta no Mercado Livre →
                    </a>
                </div>
            </div>
            
            <!-- Especificações -->
            <section style="margin-bottom: 40px;">
                <h2 style="font-size: 22px; border-bottom: 2px solid #0f766e; padding-bottom: 10px; margin-bottom: 20px;">
                    Especificações do Produto
                </h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #f5f5f5;">
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold; width: 30%;">Categoria</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{category.title()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">Preço Atual</td>
                        <td style="padding: 12px; border: 1px solid #ddd; color: #d32f2f; font-weight: bold;">{product.get('current_price', 'Consulte')}</td>
                    </tr>
                    <tr style="background: #f5f5f5;">
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">Preço Original</td>
                        <td style="padding: 12px; border: 1px solid #ddd;"><s>{product.get('original_price', 'N/A')}</s></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">Desconto</td>
                        <td style="padding: 12px; border: 1px solid #ddd; color: #388e3c; font-weight: bold;">{product.get('discount', '0%')}</td>
                    </tr>
                </table>
            </section>
            
            <!-- Análise e Conversão -->
            <section style="margin-bottom: 40px;">
                <h2 style="font-size: 22px; border-bottom: 2px solid #0f766e; padding-bottom: 10px; margin-bottom: 20px;">
                    Análise do Especialista Ninja
                </h2>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-bottom:30px;">
                    <div style="background:#f0fff4; padding:20px; border-radius:12px; border-left:5px solid #22c55e;">
                        <h4 style="margin:0 0 10px 0; color:#166534;">✅ Prós</h4>
                        <ul style="margin:0; padding-left:20px; font-size:14px;">
                            <li>Melhor preço dos últimos 30 dias</li>
                            <li>Vendedor com excelente reputação</li>
                            <li>Entrega Full disponível</li>
                        </ul>
                    </div>
                    <div style="background:#fff5f5; padding:20px; border-radius:12px; border-left:5px solid #ef4444;">
                        <h4 style="margin:0 0 10px 0; color:#991b1b;">❌ Contras</h4>
                        <ul style="margin:0; padding-left:20px; font-size:14px;">
                            <li>Estoque limitado</li>
                            <li>Alta demanda nas últimas horas</li>
                        </ul>
                    </div>
                </div>
                
                <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; border-left: 4px solid #388e3c; margin-bottom: 20px;">
                    <strong style="color: #2e7d32;">🏆 VEREDITO: MELHOR CUSTO-BENEFÍCIO</strong>
                    <p style="margin: 10px 0 0 0; color: #333;">
                        Se você busca economia sem abrir mão da qualidade, esta é a escolha certa hoje.
                    </p>
                </div>
            </section>

            <!-- Alternativas Recomendadas -->
            <section style="margin-bottom: 40px; background:#f8fafc; padding:25px; border-radius:16px;">
                <h3 style="margin-top:0;">🎯 Melhores Alternativas</h3>
                <p style="font-size:14px; color:#64748b;">Não era o que buscava? Veja estas opções:</p>
                <div style="display:flex; gap:15px; overflow-x:auto; padding-bottom:10px;">
                    <!-- Blocos dinâmicos seriam inseridos aqui -->
                    <div style="min-width:150px; background:white; padding:10px; border-radius:8px; border:1px solid #e2e8f0; text-align:center;">
                        <span style="font-size:10px; background:#dcfce7; color:#166534; padding:2px 6px; border-radius:10px;">MAIS BARATO</span>
                        <div style="height:80px; margin:10px 0; background:#eee; border-radius:4px;"></div>
                        <div style="font-size:12px; font-weight:bold;">Opção Econômica</div>
                    </div>
                    <div style="min-width:150px; background:white; padding:10px; border-radius:8px; border:1px solid #e2e8f0; text-align:center;">
                        <span style="font-size:10px; background:#f1f5f9; color:#475569; padding:2px 6px; border-radius:10px;">PREMIUM</span>
                        <div style="height:80px; margin:10px 0; background:#eee; border-radius:4px;"></div>
                        <div style="font-size:12px; font-weight:bold;">Opção Top de Linha</div>
                    </div>
                </div>
            </section>
            
            <!-- CTA -->
            <div style="background: #0f766e; color: white; padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 40px;">
                <h3 style="margin-top: 0; font-size: 20px;">Aproveite Esta Oferta</h3>
                <p style="margin: 10px 0 20px 0;">Clique abaixo para ver o produto no Mercado Livre</p>
                <a href="{product.get('ml_link', '#')}" 
                   style="display: inline-block; background: white; color: #0f766e; padding: 15px 40px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                    Ver Oferta Agora →
                </a>
            </div>
            
            <!-- Informações Adicionais -->
            <section style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 40px;">
                <h3 style="margin-top: 0;">Sobre o Compara Preço</h3>
                <p style="color: #666; margin: 0;">
                    Monitoramos automaticamente os preços do Mercado Livre para trazer as melhores ofertas. 
                    Nosso robô atualiza os dados a cada hora, garantindo que você sempre tenha acesso às promoções mais recentes.
                </p>
            </section>
            
            <!-- Navegação -->
            <div style="text-align: center; border-top: 1px solid #eee; padding-top: 20px;">
                <a href="/noticias/" style="color: #0f766e; text-decoration: none; font-weight: bold; margin-right: 20px;">
                    ← Ver Blog
                </a>
                <a href="/categorias/{category}/" style="color: #0f766e; text-decoration: none; font-weight: bold;">
                    Ver Mais em {category.title()} →
                </a>
            </div>
        </article>
    </main>
    
    <footer style="background: #1a1a1a; color: white; padding: 40px 20px; text-align: center; margin-top: 60px;">
        <p style="margin: 0;">© 2026 Compara Preço. Todos os direitos reservados.</p>
        <p style="margin: 10px 0 0 0; font-size: 12px; color: #999;">
            Somos afiliados do Mercado Livre. Ganhamos comissão por vendas realizadas através de nossos links.
        </p>
    </footer>
</body>
</html>"""
    
    return html, f"ofertas/{category}/{product_slug}.html"


def generate_blog_post_enhanced(article: dict) -> tuple:
    """Gera post de blog com Schema Markup e Open Graph."""
    
    article_slug = sanitize_filename(article.get("title", "post"))
    page_url = f"{BASE_URL}/noticias/posts/{article_slug}.html"
    canonical_url = page_url
    
    # Schema
    article_schema = generate_article_schema(article, page_url)
    org_schema = generate_organization_schema()
    
    description = article.get("description", "")[:160]
    title = f"{article.get('title', 'Post')} - Compara Preço"
    image = article.get("image", f"{BASE_URL}/assets/og-default.png")
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    
    <!-- Canonical -->
    <link rel="canonical" href="{canonical_url}">
    
    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{image}">
    <meta property="og:url" content="{page_url}">
    <meta property="article:published_time" content="{article.get('date', NOW)}">
    <meta property="article:author" content="Compara Preço">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{image}">
    
    <!-- Schema -->
    <script type="application/ld+json">
    {article_schema}
    </script>
    <script type="application/ld+json">
    {org_schema}
    </script>
    
    <meta name="google-adsense-account" content="ca-pub-4896859041377751">
    <link rel="stylesheet" href="../../assets/css/style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <a href="/" class="logo">📊 Compara Preço</a>
        </div>
    </header>
    
    <main class="container" style="padding: 40px 20px; max-width: 800px; margin: 0 auto;">
        <article>
            <header style="margin-bottom: 30px; border-bottom: 2px solid #0f766e; padding-bottom: 20px;">
                <div style="color: #0f766e; font-weight: bold; font-size: 12px; margin-bottom: 10px; text-transform: uppercase;">
                    BLOG • {article.get('category', 'NOTÍCIA')}
                </div>
                <h1 style="margin: 0; font-size: 28px; color: #1a1a1a;">{article.get('title', 'Post')}</h1>
                <p style="color: #666; margin-top: 10px; font-size: 14px;">
                    Equipe Compara Preço | {article.get('date', NOW)}
                </p>
            </header>
            
            <img src="{image}" 
                 alt="{article.get('title', 'Post')}"
                 style="width: 100%; max-height: 400px; object-fit: cover; border-radius: 8px; margin-bottom: 30px;">
            
            <div style="line-height: 1.8; color: #333; font-size: 16px;">
                {article.get('content', '<p>Conteúdo do artigo</p>')}
            </div>
            
            <div style="margin-top: 40px; text-align: center; border-top: 1px solid #eee; padding-top: 20px;">
                <a href="/noticias/" style="color: #0f766e; text-decoration: none; font-weight: bold;">
                    ← Voltar ao Blog
                </a>
            </div>
        </article>
    </main>
    
    <footer style="background: #1a1a1a; color: white; padding: 40px 20px; text-align: center; margin-top: 60px;">
        <p style="margin: 0;">© 2026 Compara Preço. Todos os direitos reservados.</p>
    </footer>
</body>
</html>"""
    
    return html, f"noticias/posts/{article_slug}.html"


if __name__ == "__main__":
    print("✅ Script de geração de páginas melhorado carregado")
    print("   - Schema Markup (Product, Article, Organization)")
    print("   - Open Graph Tags")
    print("   - Canonical Tags")
    print("   - Alt Tags em imagens")
    print("   - Breadcrumbs")
    print("   - Pronto para Google AdSense")
