import json
import os
from pathlib import Path
from typing import Any, Dict, List

from logger import logger
from quality_utils import clean_product_name, escape_attr, escape_html, money, slugify, title_from_html

ROOT = Path(__file__).resolve().parents[1] if "__file__" in locals() else Path(".")
BASE_URL = "https://comparapreco.github.io/"

CATEGORY_LABELS = {
    "celulares": "Celulares",
    "notebooks": "Notebooks",
    "monitores": "Monitores",
    "informatica": "Informática",
    "tv-e-video": "TV e Vídeo",
    "eletrodomesticos": "Eletrodomésticos",
    "games": "Games",
    "gamer": "Gamer",
    "moveis": "Móveis",
    "beleza": "Beleza",
    "ferramentas": "Ferramentas",
    "casa": "Casa",
    "tecnologia": "Tecnologia",
    "outros": "Outros",
}


def _load_products(input_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(input_path):
        logger.warning(f"Banco de produtos não encontrado: {input_path}")
        return []
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return [p for p in data if isinstance(p, dict) and p.get("status", "active") == "active"]
    except Exception as exc:
        logger.error(f"Erro ao carregar {input_path}: {exc}")
    return []


def _offer_url(product: Dict[str, Any]) -> str:
    cat = product.get("custom_category_slug") or "outros"
    p_id = product.get("id") or "produto"
    return f"/ofertas/{cat}/{slugify(product.get('name') or product.get('title'))}-{p_id}.html"


def _render_featured_products(products: List[Dict[str, Any]], limit: int = 12) -> str:
    ranked = sorted(
        products,
        key=lambda p: (float(p.get("quality_score") or 0), float(p.get("custom_discount_pct") or 0), float(p.get("price") or 0)),
        reverse=True,
    )[:limit]
    cards = []
    for product in ranked:
        name = clean_product_name(product.get("name") or product.get("title"), 82)
        image = product.get("image") or product.get("thumbnail") or ""
        discount = int(float(product.get("custom_discount_pct") or 0))
        current = money(product.get("price"))
        original = money(product.get("originalPrice") or product.get("original_price"))
        saving_html = ""
        try:
            saving = float(product.get("originalPrice") or product.get("original_price") or 0) - float(product.get("price") or 0)
            if saving > 0:
                saving_html = f'<div class="savings">Economize {money(saving)}</div>'
        except Exception:
            saving_html = ""
        cards.append(f"""
        <article class="product-card">
            <div class="badges"><span class="badge best">Melhor Preço</span>{f'<span class="badge hot">-{discount}%</span>' if discount else ''}</div>
            <a href="{_offer_url(product)}" aria-label="Ver análise de {escape_attr(name)}">
                <div class="card-img"><img src="{escape_attr(image)}" alt="{escape_attr(name)}" loading="lazy"></div>
                <h3>{escape_html(name)}</h3>
            </a>
            <div class="old-price">{original if original != 'Preço indisponível' else ''}</div>
            <div class="price-tag">{current}</div>
            {saving_html}
            <a href="{_offer_url(product)}" class="btn">Ver Oferta Ninja 🚀</a>
        </article>
        """)
    return "\n".join(cards)


def _render_recent_posts(limit: int = 8) -> str:
    posts_dir = ROOT / "noticias" / "posts"
    if not posts_dir.exists():
        return ""
    posts_html = []
    posts = sorted(posts_dir.glob("*.html"), key=os.path.getmtime, reverse=True)[:limit]
    for post in posts:
        try:
            content = post.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            content = ""
        title = title_from_html(content, post.stem)
        posts_html.append(f'<li><a href="/noticias/posts/{post.name}">{escape_html(title)}</a></li>')
    return "\n".join(posts_html)


def _render_categories() -> str:
    cat_dir = ROOT / "categorias"
    if not cat_dir.exists():
        return ""
    items = []
    for directory in sorted(d for d in cat_dir.iterdir() if d.is_dir()):
        label = CATEGORY_LABELS.get(directory.name, directory.name.replace("-", " ").title())
        items.append(f'<li><a href="/categorias/{directory.name}/" style="color: inherit; text-decoration: none;">{escape_html(label)}</a></li>')
    return "\n".join(items)


def build_homepage(input_path: str, template_path: str, output_path: str) -> None:
    logger.info("Construindo home com qualidade editorial e cards server-side...")
    if not os.path.exists(template_path):
        logger.error(f"Template {template_path} não encontrado!")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    products = _load_products(input_path)
    featured_html = _render_featured_products(products)
    recent_posts_html = _render_recent_posts()
    categories_html = _render_categories()

    template = template.replace("<!-- RECENT_POSTS_PLACEHOLDER -->", recent_posts_html)
    template = template.replace("<!-- ALL_CATEGORIES_PLACEHOLDER -->", categories_html)
    if '<div class="products-grid" id="featuredGrid"></div>' in template:
        template = template.replace('<div class="products-grid" id="featuredGrid"></div>', f'<div class="products-grid" id="featuredGrid">\n{featured_html}\n</div>')
    else:
        template = template.replace('id="featuredGrid"></div>', f'id="featuredGrid">\n{featured_html}\n</div>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template)

    logger.info(f"Home gerada com sucesso: {len(products)} produtos avaliados, {recent_posts_html.count('<li>')} posts recentes.")


if __name__ == "__main__":
    build_homepage("data/database/all_products.json", "templates/index.html", "index.html")
