import html
import json
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
    AI_ENABLED = True
except Exception:
    AI_ENABLED = False

from logger import logger

BASE_URL = "https://comparapreco.github.io/"
ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "noticias" / "posts"
NEWS_INDEX = ROOT / "noticias" / "index.html"
PRODUCTS_FILE = ROOT / "data" / "database" / "all_products.json"


def slugify(text: str, max_len: int = 90) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:max_len].strip("-") or "oferta"


def money(value: Any) -> str:
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return "Preço indisponível"


def load_products() -> List[Dict[str, Any]]:
    if not PRODUCTS_FILE.exists():
        logger.error(f"Banco de dados de produtos não encontrado: {PRODUCTS_FILE}")
        return []
    with PRODUCTS_FILE.open("r", encoding="utf-8") as f:
        products = json.load(f)
    active = [p for p in products if p.get("status", "active") == "active" and p.get("name")]
    active.sort(key=lambda p: float(p.get("custom_discount_pct") or 0), reverse=True)
    return active


def select_products(products: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
    if not products:
        return []
    existing_count = len(list(POSTS_DIR.glob("*.html"))) if POSTS_DIR.exists() else 0
    selected: List[Dict[str, Any]] = []
    for i in range(count):
        selected.append(products[(existing_count + i) % len(products)])
    return selected


def generate_product_specs(product: Dict[str, Any]) -> Dict[str, str]:
    name = product.get("name", "Produto")
    specs = {
        "Produto": name,
        "Categoria": product.get("custom_category_slug", "geral").replace("-", " ").title(),
        "Preço atual": money(product.get("price")),
        "Preço anterior": money(product.get("originalPrice") or product.get("original_price")),
        "Desconto monitorado": f"{product.get('custom_discount_pct', 0)}%",
    }
    lower_name = name.lower()
    storage = re.search(r"(\d+\s?gb|\d+\s?tb)", lower_name)
    if storage:
        specs["Armazenamento citado"] = storage.group(1).upper().replace(" ", "")
    screen = re.search(r"(\d+(?:[,.]\d+)?)\s?(?:polegadas|\")", lower_name)
    if screen:
        specs["Tela citada"] = f"{screen.group(1)} polegadas"
    return specs


def generate_ai_content(product: Dict[str, Any]) -> Optional[str]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not AI_ENABLED or not api_key:
        return None
    try:
        client = OpenAI(api_key=api_key)
        prompt = (
            "Escreva uma análise curta, objetiva e original para o blog Compara Preço sobre "
            f"o produto {product.get('name')}. O desconto atual é de "
            f"{product.get('custom_discount_pct')}% e o preço é {money(product.get('price'))}. "
            "Use português do Brasil, tom editorial, sem promessas absolutas, em 3 parágrafos. "
            "Responda apenas com HTML simples usando parágrafos."
        )
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as exc:
        logger.warning(f"IA indisponível para artigo; usando texto determinístico. Motivo: {exc}")
        return None


def generate_long_content(product: Dict[str, Any]) -> str:
    name = html.escape(product.get("name", "Produto"))
    discount = html.escape(str(product.get("custom_discount_pct", 0)))
    category = html.escape(product.get("custom_category_slug", "geral").replace("-", " "))
    specs = generate_product_specs(product)
    specs_html = "".join(f"<li><strong>{html.escape(k)}:</strong> {html.escape(v)}</li>" for k, v in specs.items())
    ai_text = generate_ai_content(product)
    intro = ai_text or (
        f"<p>O <strong>{name}</strong> entrou no radar do Compara Preço porque combina desconto relevante, "
        "preço competitivo e procura recorrente entre consumidores que acompanham ofertas do Mercado Livre.</p>"
    )
    return f"""
        {intro}
        <h2>Por que esta oferta foi selecionada?</h2>
        <p>Nosso robô prioriza produtos ativos com maior redução percentual, disponibilidade pública e potencial de economia. Nesta análise, o destaque é o desconto de <strong>{discount}%</strong> na categoria <strong>{category}</strong>.</p>
        <h2>Resumo técnico e comercial</h2>
        <ul>{specs_html}</ul>
        <h2>Pontos de atenção antes de comprar</h2>
        <p>Antes de concluir a compra, confira o prazo de entrega, a reputação do vendedor, as condições de garantia e se o preço final ainda corresponde ao valor exibido no momento da análise.</p>
        <h2>Veredito do Radar Ninja</h2>
        <p>Esta é uma oferta que merece acompanhamento porque apresenta desconto expressivo em relação ao preço de referência cadastrado. Se o produto atende à sua necessidade, vale comparar rapidamente com alternativas da mesma categoria antes que o valor mude.</p>
    """


def render_post(product: Dict[str, Any], now: datetime, sequence: int) -> tuple[str, str, str]:
    product_name = product.get("name", "Produto")
    safe_name = html.escape(product_name)
    product_id = str(product.get("id", "produto"))
    timestamp = now.strftime("%Y%m%d%H%M%S")
    slug = f"analise-{slugify(product_name, 55)}-{product_id}-{timestamp}-{sequence}"
    title = f"Análise: {product_name} vale a pena com {product.get('custom_discount_pct', 0)}% OFF?"
    canonical = f"{BASE_URL}noticias/posts/{slug}.html"
    article_body = generate_long_content(product)
    image = html.escape(product.get("image") or product.get("thumbnail") or "")
    offer_url = html.escape(product.get("custom_affiliate_url") or product.get("permalink") or "#")
    content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} | Compara Preço</title>
    <meta name="description" content="Análise automática do Radar Ninja sobre {safe_name}, preço, desconto e pontos de atenção antes de comprar.">
    <link rel="canonical" href="{canonical}">
    <link rel="alternate" type="application/rss+xml" title="Compara Preço - Feed" href="{BASE_URL}feed.xml">
    <link rel="stylesheet" href="../../assets/css/style.css">
</head>
<body>
    <header class="header"><div class="container"><a href="../../" class="logo">📊 Compara Preço</a></div></header>
    <main class="container" style="padding: 40px 20px; max-width: 860px; margin: 0 auto;">
        <article>
            <header style="margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px;">
                <div style="color: var(--primary); font-weight: bold; margin-bottom: 10px;">ANÁLISE AUTOMÁTICA DO RADAR NINJA</div>
                <h1>{html.escape(title)}</h1>
                <p style="color: #666;">Equipe Compara Preço | {now.strftime('%d/%m/%Y %H:%M')}</p>
            </header>
            <section style="background: #f9f9f9; padding: 20px; border-radius: 12px; display: flex; gap: 20px; align-items: center; margin-bottom: 30px; flex-wrap: wrap;">
                <img src="{image}" alt="{safe_name}" style="width: 160px; height: 160px; object-fit: contain; background: white; border-radius: 8px;">
                <div>
                    <div style="font-size: 26px; font-weight: 800; color: #d32f2f;">{money(product.get('price'))}</div>
                    <div style="color: #388e3c; font-weight: bold;">{html.escape(str(product.get('custom_discount_pct', 0)))}% OFF monitorado</div>
                    <a href="{offer_url}" class="btn" style="margin-top: 15px; display: inline-block;">Ver Oferta no Mercado Livre</a>
                </div>
            </section>
            <div class="content">{article_body}</div>
            <footer style="margin-top: 40px; text-align: center; border-top: 1px solid #eee; padding-top: 20px;">
                <a href="../../noticias/" style="color: var(--primary); text-decoration: none; font-weight: bold;">← Ver todas as notícias</a>
            </footer>
        </article>
    </main>
</body>
</html>
"""
    return title, slug, content


def update_news_index(title: str, slug: str, product: Dict[str, Any], now: datetime) -> None:
    if not NEWS_INDEX.exists():
        logger.warning(f"Índice de notícias não encontrado: {NEWS_INDEX}")
        return
    content = NEWS_INDEX.read_text(encoding="utf-8")
    url = f"posts/{slug}.html"
    if url in content:
        logger.info(f"Post já estava indexado: {url}")
        return
    entry = {
        "id": int(now.timestamp()),
        "tag": "analise",
        "tagLabel": "📊 Análise",
        "tagClass": "tag-analise",
        "icon": "🔍",
        "title": title,
        "excerpt": f"Análise automática do Radar Ninja sobre {product.get('name', 'produto')[:80]} com {product.get('custom_discount_pct', 0)}% de desconto monitorado.",
        "date": now.strftime("%d %b %Y"),
        "readTime": "5 min",
        "featured": True,
        "url": url,
    }
    serialized = json.dumps(entry, ensure_ascii=False, indent=8)
    marker = "const NEWS = ["
    if marker not in content:
        logger.warning("Marcador const NEWS = [ não encontrado; índice não atualizado.")
        return
    content = content.replace(marker, f"{marker}\n        {serialized},", 1)
    NEWS_INDEX.write_text(content, encoding="utf-8")


def generate_blog_content(count: int = 1) -> List[Path]:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    products = load_products()
    selected = select_products(products, count)
    created: List[Path] = []
    now = datetime.now()
    for sequence, product in enumerate(selected, start=1):
        title, slug, content = render_post(product, now, sequence)
        file_path = POSTS_DIR / f"{slug}.html"
        file_path.write_text(content, encoding="utf-8")
        update_news_index(title, slug, product, now)
        created.append(file_path)
        logger.info(f"Artigo gerado: {file_path.relative_to(ROOT)}")
    logger.info(f"Total de artigos gerados nesta execução: {len(created)}")
    return created


if __name__ == "__main__":
    import sys

    count = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("BLOG_POST_COUNT", "1"))
    generate_blog_content(max(1, count))
