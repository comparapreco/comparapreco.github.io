"""
fix_images_phase3.py
Fase 3: Correção dos casos com dados completamente misturados.

Problemas identificados:
1. MLB63040715: Nome="Furadeira Bosch" mas permalink=TV Philco 43" e imagem=697288 (errada)
   → O ID MLB63040715 pertence à TV Philco 43". Corrigir nome e imagem.
2. MLB27472599: Nome="Galaxy Buds Core" mas permalink=Projetor Maxnova e imagem=617570 (errada)
   → Dados completamente misturados. Usar dados do curated (MLB5783097440 = Galaxy Buds).
3. MLB49822404, MLB3619526469, MLB22845568: Sem imagem e sem permalink.
   → Remover do banco (sem dados suficientes para exibição correta).
4. Corrigir o script fetch_products_realtime.py para evitar que o problema se repita.
5. Adicionar proteção no sync_database.py para não aceitar produtos sem imagem.
"""
import json
import os
import re
import shutil
from datetime import datetime

try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

DATABASE_FILE = "data/database/all_products.json"
CURATED_FILE = "data/curated_products.json"
OFFERS_DIR = "ofertas"

WRONG_IMAGE_IDS = {"697288", "617570", "640641"}


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[áàãâä]', 'a', text)
    text = re.sub(r'[éèêë]', 'e', text)
    text = re.sub(r'[íìîï]', 'i', text)
    text = re.sub(r'[óòõôö]', 'o', text)
    text = re.sub(r'[úùûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[ñ]', 'n', text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text.strip())
    text = re.sub(r'-+', '-', text)
    return text[:100]


def remove_html_page(pid: str, name: str, cat: str):
    """Remove a página HTML de um produto."""
    slug = slugify(name)
    html_path = os.path.join(OFFERS_DIR, cat, f"{slug}-{pid}.html")
    if os.path.exists(html_path):
        os.remove(html_path)
        logger.info(f"HTML removido: {html_path}")
        return True
    # Busca alternativa
    cat_dir = os.path.join(OFFERS_DIR, cat)
    if os.path.exists(cat_dir):
        for fname in os.listdir(cat_dir):
            if pid in fname:
                os.remove(os.path.join(cat_dir, fname))
                logger.info(f"HTML removido: {os.path.join(cat_dir, fname)}")
                return True
    return False


def main():
    logger.info("=== Fase 3: Correção de dados misturados e casos residuais ===")

    with open(DATABASE_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    with open(CURATED_FILE, "r", encoding="utf-8") as f:
        curated = json.load(f)

    curated_map = {p["id"]: p for p in curated}

    logger.info(f"Total inicial: {len(products)} produtos")

    # ===== CORREÇÃO 1: MLB63040715 =====
    # ID MLB63040715 pertence à TV Philco 43" P43VIK (conforme permalink)
    # Nome "Furadeira Bosch" foi misturado erroneamente
    # Imagem 697288 é errada para este produto
    # Usar dados do curated MLB4367472775 (TV Philco 43) como referência de imagem
    p63 = next((p for p in products if p["id"] == "MLB63040715"), None)
    if p63:
        # A imagem correta da TV Philco 43" P43VIK
        # Buscando no curated a TV Philco 43 com o mesmo permalink
        tv_philco_curated = next(
            (p for p in curated if "philco" in p.get("name", "").lower() and "43" in p.get("name", "") and "p43vik" in p.get("name", "").lower()),
            None
        )
        if tv_philco_curated:
            correct_img = tv_philco_curated.get("image", "")
            # A imagem do curated também é 697288 - está errada lá também
            # Vamos usar a imagem de outro produto Philco 43 que temos no banco
            pass

        # Buscar no banco produtos Philco 43 com imagem válida
        philco_43_with_img = [
            p for p in products
            if "philco" in p.get("name", "").lower()
            and "43" in p.get("name", "")
            and p.get("image", "")
            and not any(w in p.get("image", "") for w in WRONG_IMAGE_IDS)
        ]

        if philco_43_with_img:
            # Usar imagem de outro Philco 43 como referência
            ref_img = philco_43_with_img[0].get("image", "")
            logger.info(f"MLB63040715: usando imagem de referência Philco 43: {ref_img[:60]}")
        else:
            # Imagem da TV Philco 43 P43VIK do banco de dados
            ref_img = "https://http2.mlstatic.com/D_NQ_NP_902043-MLA96988011016_112025-O.webp"
            logger.info(f"MLB63040715: usando imagem hardcoded Philco 43: {ref_img[:60]}")

        # Corrigir nome para refletir o produto correto (TV Philco 43 P43VIK)
        old_name = p63.get("name", "")
        p63["name"] = "Smart TV Philco 43\" P43VIK Full HD LED Roku"
        p63["title"] = "Smart TV Philco 43\" P43VIK Full HD LED Roku"
        p63["image"] = ref_img
        p63["thumbnail"] = ref_img
        p63["image_url"] = ref_img
        p63["custom_category_slug"] = "tv-e-video"
        logger.info(f"✅ MLB63040715: corrigido '{old_name}' → '{p63['name']}'")
        logger.info(f"   Imagem: {ref_img[:60]}")

    # ===== CORREÇÃO 2: MLB27472599 =====
    # Nome="Galaxy Buds Core" mas permalink=Projetor Maxnova
    # Usar dados do curated MLB5783097440 (Galaxy Buds Core) como referência
    p27 = next((p for p in products if p["id"] == "MLB27472599"), None)
    if p27:
        galaxy_buds_curated = curated_map.get("MLB5783097440")
        if galaxy_buds_curated:
            correct_img = galaxy_buds_curated.get("image", "")
            # Converter para versão sem 2X
            correct_img = correct_img.replace("D_Q_NP_2X_", "D_NQ_NP_").replace("-AB.webp", "-O.webp")
            p27["image"] = correct_img
            p27["thumbnail"] = correct_img
            p27["image_url"] = correct_img
            logger.info(f"✅ MLB27472599: imagem corrigida para Galaxy Buds: {correct_img[:60]}")
        else:
            # Imagem hardcoded do Galaxy Buds Core
            correct_img = "https://http2.mlstatic.com/D_NQ_NP_650858-MLA97317826023_112025-O.webp"
            p27["image"] = correct_img
            p27["thumbnail"] = correct_img
            p27["image_url"] = correct_img
            logger.info(f"✅ MLB27472599: imagem hardcoded Galaxy Buds: {correct_img[:60]}")

    # ===== CORREÇÃO 3: Remover produtos sem imagem e sem permalink =====
    # MLB49822404, MLB3619526469, MLB22845568 - sem dados suficientes
    ids_to_remove = {"MLB49822404", "MLB3619526469", "MLB22845568"}
    products_final = []
    for p in products:
        pid = p.get("id", "")
        if pid in ids_to_remove:
            name = p.get("name", "") or p.get("title", "")
            cat = p.get("custom_category_slug", "outros")
            remove_html_page(pid, name, cat)
            logger.info(f"Removido produto sem imagem/permalink: {pid} | {name[:50]}")
        else:
            products_final.append(p)

    logger.info(f"Produtos removidos (sem imagem/permalink): {len(products) - len(products_final)}")

    # ===== SALVAR =====
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(products_final, f, ensure_ascii=False, indent=2)

    # ===== DIAGNÓSTICO FINAL =====
    from collections import Counter
    images = [p.get("image", "") for p in products_final]
    thumbs = [p.get("thumbnail", "") for p in products_final]

    wrong_img = [p for p in products_final if any(w in p.get("image", "") for w in WRONG_IMAGE_IDS)]
    no_img = [p for p in products_final if not p.get("image", "").strip()]

    img_count = Counter(images)
    thumb_count = Counter(thumbs)

    logger.info(f"\n=== DIAGNÓSTICO FINAL ===")
    logger.info(f"Total produtos: {len(products_final)}")
    logger.info(f"Images únicas: {len(set(images))}")
    logger.info(f"Thumbnails únicos: {len(set(thumbs))}")
    logger.info(f"Produtos sem imagem: {len(no_img)}")
    logger.info(f"Produtos com imagem errada (697288/617570): {len(wrong_img)}")

    if wrong_img:
        for p in wrong_img:
            logger.warning(f"  Ainda errado: {p['id']} | {p.get('name','?')[:50]} | {p.get('image','')[:60]}")

    logger.info("\nTop 5 images repetidas:")
    for img, c in img_count.most_common(5):
        if c > 1:
            logger.info(f"  {c}x: {img[:80]}")

    logger.info("\nTop 5 thumbnails repetidos:")
    for t, c in thumb_count.most_common(5):
        if c > 1:
            logger.info(f"  {c}x: {t[:80]}")

    # Verificar sincronização image == thumbnail
    synced = sum(1 for p in products_final if p.get("image") and p.get("image") == p.get("thumbnail"))
    logger.info(f"\nProdutos com image == thumbnail: {synced}/{len(products_final)}")

    logger.info("=== Fase 3 concluída ===")


if __name__ == "__main__":
    main()
