import os
import json
import unicodedata
import random
from pathlib import Path
from logger import logger

ROOT = Path(__file__).resolve().parents[1] if "__file__" in locals() else Path(".")
BASE_URL = "https://comparapreco.github.io/"

def build_homepage(input_path, template_path, output_path):
    logger.info(f"Construindo home com links internos de SEO...")
    if not os.path.exists(template_path):
        logger.error(f"Template {template_path} não encontrado!")
        return
    
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # 1. Carregar posts para seção de análises (Eliminar Páginas Órfãs)
    posts_dir = ROOT / "noticias" / "posts"
    posts_html = ""
    if posts_dir.exists():
        posts = sorted(list(posts_dir.glob("*.html")), key=os.path.getmtime, reverse=True)[:8]
        for p in posts:
            title = p.stem.replace("analise-", "").replace("-", " ").title()
            posts_html += f'<li><a href="/noticias/posts/{p.name}">{title}</a></li>\n'
    
    template = template.replace("<!-- RECENT_POSTS_PLACEHOLDER -->", posts_html)

    # 2. Carregar todas as categorias para o rodapé (Melhorar Linkagem Interna)
    cat_dir = ROOT / "categorias"
    cat_html = ""
    if cat_dir.exists():
        cats = sorted([d.name for d in cat_dir.iterdir() if d.is_dir()])
        for c in cats:
            name = c.replace("-", " ").title()
            cat_html += f'<li><a href="/categorias/{c}/" style="color: inherit; text-decoration: none;">{name}</a></li>\n'
    
    template = template.replace("<!-- ALL_CATEGORIES_PLACEHOLDER -->", cat_html)

    # 3. Processar produtos (Original)
    products = []
    if os.path.exists(input_path):
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                products = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar {input_path}: {e}")

    # Salvar a home final
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template)
    
    logger.info("Home gerada com sucesso e links de SEO injetados.")

if __name__ == "__main__":
    build_homepage("data/database/all_products.json", "templates/index.html", "index.html")
