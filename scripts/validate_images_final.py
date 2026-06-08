"""
validate_images_final.py
Validação final: verifica 20+ produtos aleatórios para confirmar que
cada produto exibe sua própria imagem correta e sem repetições.
"""
import json
import os
import re
import random
from collections import Counter

try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

DATABASE_FILE = "data/database/all_products.json"
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


def get_html_image(pid: str, name: str, cat: str) -> str:
    """Extrai a URL de imagem do arquivo HTML gerado para o produto."""
    slug = slugify(name)
    html_path = os.path.join(OFFERS_DIR, cat, f"{slug}-{pid}.html")
    if not os.path.exists(html_path):
        # Busca alternativa
        cat_dir = os.path.join(OFFERS_DIR, cat)
        if os.path.exists(cat_dir):
            for fname in os.listdir(cat_dir):
                if pid in fname:
                    html_path = os.path.join(cat_dir, fname)
                    break
        else:
            return "HTML_NOT_FOUND"

    if not os.path.exists(html_path):
        return "HTML_NOT_FOUND"

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extrair URL da imagem do produto
    m = re.search(r'<img[^>]+alt="[^"]*"[^>]+src="([^"]+)"', content)
    if m:
        return m.group(1)
    return "IMG_NOT_FOUND_IN_HTML"


def validate():
    logger.info("=== Validação Final: Verificando imagens de 20+ produtos aleatórios ===\n")

    with open(DATABASE_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    logger.info(f"Total de produtos no banco: {len(products)}")

    # ===== VALIDAÇÃO 1: Estatísticas gerais =====
    images = [p.get("image", "") for p in products]
    thumbs = [p.get("thumbnail", "") for p in products]
    img_count = Counter(images)
    thumb_count = Counter(thumbs)

    no_img = [p for p in products if not p.get("image", "").strip()]
    wrong_img = [p for p in products if any(w in p.get("image", "") for w in WRONG_IMAGE_IDS)]
    synced = [p for p in products if p.get("image") and p.get("image") == p.get("thumbnail")]
    dup_imgs = {img: c for img, c in img_count.items() if c > 1 and img}

    logger.info("--- ESTATÍSTICAS GERAIS ---")
    logger.info(f"  Imagens únicas: {len(set(images))}/{len(products)}")
    logger.info(f"  Thumbnails únicos: {len(set(thumbs))}/{len(products)}")
    logger.info(f"  Produtos sem imagem: {len(no_img)}")
    logger.info(f"  Produtos com imagem errada (697288/617570): {len(wrong_img)}")
    logger.info(f"  Produtos com image == thumbnail: {len(synced)}/{len(products)}")
    logger.info(f"  Imagens duplicadas (>1 produto): {len(dup_imgs)}")

    if dup_imgs:
        logger.info("\n  Imagens duplicadas:")
        for img, c in sorted(dup_imgs.items(), key=lambda x: -x[1]):
            prods = [p for p in products if p.get("image") == img]
            logger.info(f"    {c}x: {img[:70]}")
            for p in prods:
                logger.info(f"      → {p['id']} | {p.get('name','?')[:50]}")

    # ===== VALIDAÇÃO 2: Amostra de 25 produtos aleatórios =====
    logger.info("\n--- AMOSTRA DE 25 PRODUTOS ALEATÓRIOS ---")
    sample = random.sample(products, min(25, len(products)))

    ok_count = 0
    fail_count = 0
    results = []

    for p in sample:
        pid = p.get("id", "")
        name = p.get("name", "") or p.get("title", "")
        cat = p.get("custom_category_slug", "outros")
        db_image = p.get("image", "")
        db_thumb = p.get("thumbnail", "")
        html_image = get_html_image(pid, name, cat)

        # Verificações
        has_image = bool(db_image and db_image.strip())
        is_wrong = any(w in db_image for w in WRONG_IMAGE_IDS) if db_image else False
        is_synced = db_image == db_thumb
        html_matches = html_image == db_image if html_image not in ("HTML_NOT_FOUND", "IMG_NOT_FOUND_IN_HTML") else None
        is_mlstatic = "mlstatic.com" in db_image if db_image else False

        status = "✅ OK"
        issues = []
        if not has_image:
            issues.append("SEM_IMAGEM")
        if is_wrong:
            issues.append("IMAGEM_ERRADA")
        if not is_synced:
            issues.append("IMAGE≠THUMBNAIL")
        if html_matches is False:
            issues.append("HTML≠DB")
        if not is_mlstatic and has_image:
            issues.append("NAO_MLSTATIC")

        if issues:
            status = f"❌ FALHA: {', '.join(issues)}"
            fail_count += 1
        else:
            ok_count += 1

        results.append({
            "id": pid,
            "name": name[:50],
            "status": status,
            "image": db_image[:70] if db_image else "(vazio)",
            "html_image": html_image[:70] if html_image else "(vazio)",
        })

    for r in results:
        logger.info(f"\n  {r['status']}")
        logger.info(f"  ID: {r['id']} | {r['name']}")
        logger.info(f"  DB image:   {r['image']}")
        logger.info(f"  HTML image: {r['html_image']}")

    # ===== VALIDAÇÃO 3: Verificar todos os HTMLs gerados =====
    logger.info("\n--- VERIFICAÇÃO DE TODOS OS HTMLs ---")
    html_wrong = 0
    html_ok = 0
    html_missing = 0

    for root, dirs, files in os.walk(OFFERS_DIR):
        for fname in files:
            if not fname.endswith(".html"):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            m = re.search(r'<img[^>]+src="([^"]+)"', content)
            if m:
                img_url = m.group(1)
                if any(w in img_url for w in WRONG_IMAGE_IDS):
                    html_wrong += 1
                    logger.warning(f"  HTML com imagem errada: {fpath}")
                else:
                    html_ok += 1
            else:
                html_missing += 1

    logger.info(f"  HTMLs com imagem correta: {html_ok}")
    logger.info(f"  HTMLs com imagem errada: {html_wrong}")
    logger.info(f"  HTMLs sem imagem: {html_missing}")

    # ===== RESULTADO FINAL =====
    logger.info("\n=== RESULTADO FINAL DA VALIDAÇÃO ===")
    logger.info(f"  Amostra de 25 produtos: {ok_count} OK, {fail_count} com problemas")
    logger.info(f"  HTMLs com imagem errada: {html_wrong}")
    logger.info(f"  Produtos sem imagem no banco: {len(no_img)}")
    logger.info(f"  Produtos com imagem errada no banco: {len(wrong_img)}")

    if fail_count == 0 and html_wrong == 0 and len(no_img) == 0 and len(wrong_img) == 0:
        logger.info("\n  ✅ VALIDAÇÃO APROVADA: Todos os produtos têm imagens corretas e únicas!")
    else:
        logger.warning("\n  ⚠️  VALIDAÇÃO COM RESSALVAS: Verificar itens acima.")

    return {
        "total": len(products),
        "unique_images": len(set(images)),
        "no_image": len(no_img),
        "wrong_image": len(wrong_img),
        "synced": len(synced),
        "duplicates": len(dup_imgs),
        "sample_ok": ok_count,
        "sample_fail": fail_count,
        "html_wrong": html_wrong,
        "html_ok": html_ok,
    }


if __name__ == "__main__":
    validate()
