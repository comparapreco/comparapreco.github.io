"""
fetch_products_realtime.py
Busca SEMPRE produtos NOVOS do Mercado Livre via scraping.
Ignora histórico de IDs — cada execução busca produtos diferentes.
Estratégia: varia as páginas, termos de busca e categorias para encontrar
sempre produtos novos e diferentes.
"""

import os
import json
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Any, Dict, List

try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

RAW_DATA_FILE = "data/raw_products.json"
BLACKLIST_FILE = "data/blacklist_ids.json"

AFILIADO_ID = os.environ.get("ML_AFILIADO_ID", "vendas0nline")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
    "Referer": "https://www.mercadolivre.com.br/",
    "Connection": "keep-alive",
}

# Estratégia de busca: múltiplas páginas e categorias
# Cada execução varia a página para encontrar produtos diferentes
SEARCH_STRATEGIES = [
    # (tipo, valor, descrição)
    ("category", "MLB1051", "Celulares"),
    ("category", "MLB1648", "Informática"),
    ("category", "MLB5726", "Eletrodomésticos"),
    ("category", "MLB1144", "Games"),
    ("category", "MLB1000", "TV e Vídeo"),
    ("category", "MLB1574", "Casa"),
    ("category", "MLB1246", "Beleza"),
    ("category", "MLB1501", "Ferramentas"),
    ("search", "promoção", "Busca: Promoção"),
    ("search", "desconto", "Busca: Desconto"),
    ("search", "oferta", "Busca: Oferta"),
    ("search", "liquidação", "Busca: Liquidação"),
]

BLOCKED_TERMS = [
    "whey", "dark lab", "capinha", "película", "pelicula",
    "usado", "recondicionado", "vitrine", "quebrado", "defeito",
    "esgotado", "sem estoque", "digital", "curso", "e-book", "ebook",
    "serviço", "aluguel", "conserto", "manutenção", "instalação",
    "pdf", "link", "acesso", "conta", "premium", "assinatura"
]


def load_json(filepath: str, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def save_json(filepath: str, data):
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def classify_category(title: str) -> str:
    """Classifica o produto na categoria correta pelo título."""
    t = title.lower()
    if any(k in t for k in ["celular", "smartphone", "iphone", "galaxy", "motorola moto", "redmi", "poco"]):
        return "celulares"
    if any(k in t for k in ["notebook", "ultrabook", "macbook", "chromebook", "laptop"]):
        return "notebooks"
    if any(k in t for k in ["monitor", "tela gamer", "display 4k"]):
        return "monitores"
    if any(k in t for k in ["computador", "pc gamer", "desktop", "teclado", "mouse", "ssd", "processador", "placa de vídeo", "memória ram"]):
        return "informatica"
    if any(k in t for k in ["smart tv", "tv ", "televisão", "televisor", "projetor"]):
        return "tv-e-video"
    if any(k in t for k in ["geladeira", "fogão", "microondas", "lavadora", "máquina de lavar",
                             "ar condicionado", "fritadeira", "cafeteira", "chuveiro", "liquidificador"]):
        return "eletrodomesticos"
    if any(k in t for k in ["playstation", "xbox", "nintendo", "console", "controle", "headset gamer"]):
        return "games"
    if any(k in t for k in ["cadeira", "mesa", "sofá", "cama", "colchão", "armário", "estante", "rack"]):
        return "moveis"
    if any(k in t for k in ["perfume", "shampoo", "creme", "maquiagem", "batom", "protetor solar"]):
        return "beleza"
    if any(k in t for k in ["furadeira", "parafusadeira", "chave", "martelo", "serra", "alicate"]):
        return "ferramentas"
    return "outros"


def scrape_search(search_type: str, search_value: str, page: int = 1) -> List[Dict[str, Any]]:
    """
    Faz scraping do Mercado Livre para uma busca específica.
    search_type: "category" ou "search"
    search_value: ID da categoria ou termo de busca
    page: número da página (1-5)
    """
    if search_type == "category":
        url = f"https://www.mercadolivre.com.br/ofertas?category={search_value}&_offset={page * 40}"
    else:  # search
        url = f"https://www.mercadolivre.com.br/{search_value}?_offset={page * 40}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            logger.warning(f"HTTP {resp.status_code} para {search_value}")
            return []

        html = resp.text

        # Verificar bloqueio
        if "account-verification" in html or "suspicious-traffic" in html:
            logger.warning(f"Bloqueado por verificação para {search_value}")
            return []

        soup = BeautifulSoup(html, "html.parser")

        # Encontrar script com dados
        target_script = None
        for s in soup.find_all("script"):
            if s.string and '"items"' in s.string and "MLB" in s.string and len(s.string) > 5000:
                target_script = s.string
                break

        if not target_script:
            return []

        # Extrair dados
        metadata_list = re.findall(
            r'"product_id":"(MLB\d+)"[^}]*?"url":"([^"]+)"',
            target_script
        )
        title_list = re.findall(
            r'"type":"title"[^}]*?"text":"([^"]{5,200})"',
            target_script
        )
        price_list = re.findall(
            r'"previous_price":\{"value":(\d+),"currency":"BRL"[^}]*\},"current_price":\{"value":(\d+)',
            target_script
        )
        img_list = re.findall(
            r'"id":"(\d+-MLA\d+[^"]*)"',
            target_script
        )

        n = min(len(metadata_list), len(title_list), len(price_list), len(img_list))
        if n == 0:
            return []

        products = []
        for i in range(n):
            product_id, url_raw = metadata_list[i]
            title = title_list[i]
            prev_price = float(price_list[i][0])
            curr_price = float(price_list[i][1])
            img_id = img_list[i]

            # Bloquear por termos
            if any(term in title.lower() for term in BLOCKED_TERMS):
                continue

            permalink = "https://" + url_raw.replace("\\u002F", "/")
            permalink = permalink.split("#")[0].split("?pdp_filters")[0]
            affiliate_url = permalink + f"?matt_tool={AFILIADO_ID}"
            img_url = f"https://http2.mlstatic.com/D_NQ_NP_{img_id}-O.webp"

            discount = int(((prev_price - curr_price) / prev_price) * 100) if prev_price > curr_price else 0

            products.append({
                "id": product_id,
                "name": title,
                "price": curr_price,
                "original_price": prev_price,
                "permalink": permalink,
                "image": img_url,
                "thumbnail": img_url,
                "custom_category_slug": classify_category(title),
                "custom_discount_pct": discount,
                "custom_affiliate_url": affiliate_url,
                "status": "active",
                "data_coleta": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
            })

        return products

    except Exception as e:
        logger.warning(f"Erro ao buscar {search_value}: {e}")
        return []


def main():
    logger.info("=== Iniciando busca de produtos NOVOS (scraping ML) ===")

    blacklist = set(load_json(BLACKLIST_FILE, []))
    all_found = []
    seen_ids = set()

    # Selecionar estratégias aleatórias para variar a busca a cada execução
    strategies = random.sample(SEARCH_STRATEGIES, min(6, len(SEARCH_STRATEGIES)))
    
    for search_type, search_value, description in strategies:
        logger.info(f"Buscando: {description}")
        
        # Variar página aleatoriamente (1-3) para encontrar produtos diferentes
        page = random.randint(1, 3)
        
        products = scrape_search(search_type, search_value, page)
        logger.info(f"  Encontrados: {len(products)} produtos")

        for p in products:
            p_id = p["id"]

            # Evitar duplicatas
            if p_id in seen_ids or p_id in blacklist:
                continue

            seen_ids.add(p_id)
            all_found.append(p)

        # Pausa entre buscas
        time.sleep(random.uniform(2.0, 4.0))

    # Salvar produtos encontrados
    save_json(RAW_DATA_FILE, all_found)

    logger.info(f"=== Busca finalizada: {len(all_found)} produtos NOVOS encontrados ===")


if __name__ == "__main__":
    main()
