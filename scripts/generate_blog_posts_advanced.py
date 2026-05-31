import json
import os
from datetime import datetime
import unicodedata
from logger import logger

BASE_URL = "/"

def slugify(text: str) -> str:
    """Converte texto em slug amigável para URL."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.lower().replace(' ', '-')
    return ''.join(c for c in text if c.isalnum() or c == '-')

def calculate_reading_time(content: str) -> int:
    """Calcula tempo de leitura em minutos (média de 200 palavras/minuto)."""
    word_count = len(content.split())
    return max(1, word_count // 200)

def generate_article_schema(title: str, description: str, author: str, publish_date: str, url: str, image_url: str = "") -> str:
    """Gera schema.org para artigos (BlogPosting/NewsArticle)."""
    schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "description": description,
        "author": {
            "@type": "Person",
            "name": author
        },
        "datePublished": publish_date,
        "dateModified": publish_date,
        "url": url,
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": url
        }
    }
    
    if image_url:
        schema["image"] = {
            "@type": "ImageObject",
            "url": image_url,
            "width": 1200,
            "height": 630
        }
    
    return json.dumps(schema, ensure_ascii=False, indent=2)

def generate_breadcrumb_schema(breadcrumbs: list) -> str:
    """Gera schema.org para breadcrumbs."""
    items = []
    for idx, (name, url) in enumerate(breadcrumbs, 1):
        items.append({
            "@type": "ListItem",
            "position": idx,
            "name": name,
            "item": url
        })
    
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }
    
    return json.dumps(schema, ensure_ascii=False, indent=2)

def generate_blog_article(title: str, description: str, content: str, category: str = "Ofertas", 
                         author: str = "Radar de Preços", keywords: str = "") -> dict:
    """Gera um artigo de blog completo com E-E-A-T."""
    
    now = datetime.now()
    publish_date = now.isoformat()
    slug = slugify(title)
    reading_time = calculate_reading_time(content)
    
    # URLs
    article_url = f"{BASE_URL}noticias/posts/{slug}/"
    breadcrumbs = [
        ("Radar de Preços", f"{BASE_URL}"),
        ("Notícias", f"{BASE_URL}noticias/"),
        (title, article_url)
    ]
    
    # Schema.org
    article_schema = generate_article_schema(title, description, author, publish_date, article_url)
    breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs)
    
    # HTML completo com E-E-A-T
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Radar de Preços</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <link rel="canonical" href="{article_url}">
    <link rel="stylesheet" href="../../assets/css/style.css">
    
    <!-- Open Graph para Redes Sociais -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:url" content="{article_url}">
    <meta property="og:type" content="article">
    <meta property="article:published_time" content="{publish_date}">
    <meta property="article:author" content="{author}">
    <meta property="article:section" content="{category}">
    
    <!-- Schema.org -->
    <script type="application/ld+json">
{article_schema}
    </script>
    <script type="application/ld+json">
{breadcrumb_schema}
    </script>
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="../../" class="logo">📊 <strong>Radar de Preços</strong></a>
            <button id="themeToggle">🌙</button>
        </div>
    </header>
    
    <!-- Breadcrumb Navigation -->
    <nav class="breadcrumb" style="background: var(--card); padding: 15px 0; border-bottom: 1px solid var(--border);">
        <div class="container" style="font-size: 14px;">
            <a href="../../">Radar de Preços</a> › 
            <a href="../../noticias/">Notícias</a> › 
            <span>{title}</span>
        </div>
    </nav>
    
    <main class="container" style="padding: 40px 20px;">
        <article>
            <!-- Cabeçalho do Artigo -->
            <header style="margin-bottom: 40px; border-bottom: 2px solid var(--border); padding-bottom: 20px;">
                <h1 style="margin: 0 0 15px 0;">{title}</h1>
                <p style="margin: 0; color: var(--text-secondary); font-size: 14px;">
                    <strong>Por:</strong> {author} | 
                    <strong>Publicado:</strong> {now.strftime('%d de %B de %Y')} | 
                    <strong>Atualizado:</strong> {now.strftime('%d de %B de %Y')} | 
                    <strong>Tempo de Leitura:</strong> {reading_time} min
                </p>
            </header>
            
            <!-- Conteúdo do Artigo -->
            <div class="article-content" style="line-height: 1.8; font-size: 16px;">
                {content}
            </div>
            
            <!-- Autor Bio -->
            <div style="background: var(--card); padding: 20px; border-radius: 12px; margin-top: 40px; border-left: 4px solid var(--primary);">
                <h3 style="margin-top: 0;">Sobre o Autor</h3>
                <p><strong>{author}</strong> é uma plataforma de inteligência de preços que monitora o mercado brasileiro em tempo real, ajudando consumidores a encontrar as melhores ofertas e economizar em suas compras.</p>
            </div>
            
            <!-- CTAs -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 40px;">
                <a href="../../comparativos/" class="btn" style="text-align: center; padding: 15px;">Ver Comparativos</a>
                <a href="../../alertas/" class="btn" style="text-align: center; padding: 15px; background: var(--primary);">Criar Alerta de Preço</a>
            </div>
            
            <!-- Voltar -->
            <div style="margin-top: 40px; text-align: center;">
                <a href="../../noticias/" class="btn" style="padding: 10px 20px;">← Voltar para Notícias</a>
            </div>
        </article>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>© 2026 Radar de Preços. Inteligência de Preços em Tempo Real.</p>
            <div class="footer-links">
                <a href="../../noticias/">Blog</a>
                <a href="../../sobre/">Sobre</a>
                <a href="../../contato/">Contato</a>
                <a href="../../privacidade/">Privacidade</a>
                <a href="../../termos/">Termos</a>
            </div>
        </div>
    </footer>
    
    <script src="../../assets/js/app.js"></script>
</body>
</html>"""
    
    return {
        "title": title,
        "slug": slug,
        "description": description,
        "content": content,
        "author": author,
        "category": category,
        "keywords": keywords,
        "reading_time": reading_time,
        "publish_date": publish_date,
        "html": html_content
    }

def save_article(article: dict, posts_dir: str = "noticias/posts") -> str:
    """Salva o artigo em arquivo HTML."""
    if not os.path.exists(posts_dir):
        os.makedirs(posts_dir)
    
    file_path = os.path.join(posts_dir, f"{article['slug']}.html")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(article['html'])
    
    logger.info(f"Artigo salvo: {file_path}")
    return file_path

# Exemplo de uso
if __name__ == "__main__":
    # Artigo de exemplo
    article_content = """
    <p>Este é um artigo de exemplo com conteúdo de alta qualidade, otimizado para SEO e com E-E-A-T completo.</p>
    
    <h2>Introdução</h2>
    <p>Nesta seção, apresentamos o tópico e por que é importante para o leitor.</p>
    
    <h2>Seção Principal</h2>
    <p>Conteúdo detalhado e informativo sobre o tópico.</p>
    
    <h3>Subseção</h3>
    <p>Mais informações e insights.</p>
    
    <h2>Conclusão</h2>
    <p>Resumo dos pontos principais e chamada para ação.</p>
    """
    
    article = generate_blog_article(
        title="Como Economizar na Compra de Eletrônicos em 2026",
        description="Guia completo com 10 estratégias comprovadas para economizar ao comprar eletrônicos. Dicas de especialistas e dados reais do mercado.",
        content=article_content,
        category="Guias",
        author="Radar de Preços",
        keywords="economizar eletrônicos, dicas compras, ofertas 2026"
    )
    
    save_article(article)
