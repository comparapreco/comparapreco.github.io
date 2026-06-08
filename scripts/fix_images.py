"""
fix_images.py
Corrige o problema de imagens duplicadas no banco de dados all_products.json.

CAUSA RAIZ IDENTIFICADA:
- O campo `thumbnail` de 284 produtos contém a URL da imagem da Furadeira Bosch
  (MLB63040715 / 697288-MLA100482486016) em vez da imagem correta de cada produto.
- O campo `image_url` também está incorreto (igual ao thumbnail errado).
- O campo `image` está correto para a maioria dos produtos.
- O generate_pages.py usa `product.get("image") or product.get("thumbnail")`,
  então quando `image` está vazio, cai no `thumbnail` errado.
- Para os produtos MLB289492xxx (IDs artificiais), o campo `image` está vazio
  e o `thumbnail` contém a imagem errada.

CORREÇÃO:
1. Para produtos onde `image` está preenchido e correto: sincronizar `thumbnail`
   e `image_url` com o valor de `image`.
2. Para produtos onde `image` está vazio mas `thumbnail` tem a imagem errada:
   buscar a imagem correta via API do Mercado Livre.
3. Regenerar as páginas HTML dos produtos corrigidos.
"""
import json
import os
import re
import requests
import time
import shutil
from datetime import datetime

try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

DATABASE_FILE = "data/database/all_products.json"
BACKUP_FILE = f"data/backups/backup_before_fix_images_{datetime.now().strftime('%Y_%m_%d_%Hh')}.json"

# Imagens genéricas/erradas conhecidas que não pertencem ao produto
WRONG_IMAGE_IDS = {
    "697288",  # Furadeira Bosch MLB63040715
    "617570",  # Perfume Lattafa (imagem genérica)
    "640641",  # Imagem genérica do expand_products.py
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

ML_API_BASE = "https://api.mercadolibre.com"


def is_wrong_image(url: str) -> bool:
    """Verifica se a URL de imagem é uma das imagens genéricas/erradas."""
    if not url:
        return True
    for wrong_id in WRONG_IMAGE_IDS:
        if wrong_id in url:
            return True
    return False


def fetch_image_from_ml_api(product_id: str) -> str:
    """Busca a imagem correta do produto via API do Mercado Livre."""
    # Normalizar ID (remover hífen se houver)
    mlb_id = product_id.replace("MLB-", "MLB").replace("MLB ", "MLB")
    if not mlb_id.startswith("MLB"):
        return ""

    try:
        url = f"{ML_API_BASE}/items/{mlb_id}"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            # Tentar thumbnail primeiro (menor, mais rápido)
            thumbnail = data.get("thumbnail", "")
            # Converter para versão de alta qualidade
            if thumbnail:
                # Substituir _I. por _O. para obter imagem de melhor qualidade
                hq = thumbnail.replace("_I.", "_O.").replace("-I.", "-O.")
                return hq
            # Tentar pictures
            pictures = data.get("pictures", [])
            if pictures:
                return pictures[0].get("url", "")
        elif resp.status_code == 404:
            logger.warning(f"Produto não encontrado na API: {mlb_id}")
        else:
            logger.warning(f"API retornou {resp.status_code} para {mlb_id}")
    except Exception as e:
        logger.warning(f"Erro ao buscar imagem para {mlb_id}: {e}")

    return ""


def fix_product_images(products: list) -> tuple:
    """
    Corrige as imagens dos produtos.
    Retorna (produtos_corrigidos, lista_de_ids_corrigidos, lista_de_ids_sem_imagem)
    """
    fixed_ids = []
    no_image_ids = []
    api_calls = 0

    for p in products:
        pid = p.get("id", "")
        current_image = p.get("image", "")
        current_thumbnail = p.get("thumbnail", "")
        current_image_url = p.get("image_url", "")

        # CASO 1: image está correto, mas thumbnail/image_url estão errados
        if current_image and not is_wrong_image(current_image):
            changed = False
            if is_wrong_image(current_thumbnail) or current_thumbnail != current_image:
                p["thumbnail"] = current_image
                changed = True
            if is_wrong_image(current_image_url) or current_image_url != current_image:
                p["image_url"] = current_image
                changed = True
            if changed:
                fixed_ids.append(pid)
            continue

        # CASO 2: image está vazio ou errado — buscar via API
        logger.info(f"Buscando imagem via API para: {pid} ({p.get('name','?')[:50]})")
        api_image = fetch_image_from_ml_api(pid)
        api_calls += 1

        if api_image and not is_wrong_image(api_image):
            p["image"] = api_image
            p["thumbnail"] = api_image
            p["image_url"] = api_image
            fixed_ids.append(pid)
            logger.info(f"  ✅ Imagem corrigida: {api_image[:60]}")
        else:
            # Última tentativa: verificar se thumbnail tem algo válido que não seja errado
            if current_thumbnail and not is_wrong_image(current_thumbnail):
                p["image"] = current_thumbnail
                p["image_url"] = current_thumbnail
                fixed_ids.append(pid)
                logger.info(f"  ✅ Usando thumbnail existente: {current_thumbnail[:60]}")
            else:
                no_image_ids.append(pid)
                logger.warning(f"  ❌ Sem imagem válida para: {pid}")

        # Pausa para não sobrecarregar a API
        if api_calls % 5 == 0:
            time.sleep(1.0)
        else:
            time.sleep(0.3)

    return products, fixed_ids, no_image_ids


def main():
    logger.info("=== Iniciando correção de imagens duplicadas ===")

    # Carregar banco de dados
    if not os.path.exists(DATABASE_FILE):
        logger.error(f"Banco de dados não encontrado: {DATABASE_FILE}")
        return

    with open(DATABASE_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    logger.info(f"Total de produtos no banco: {len(products)}")

    # Diagnóstico antes da correção
    wrong_thumb = [p for p in products if is_wrong_image(p.get("thumbnail", ""))]
    wrong_image = [p for p in products if is_wrong_image(p.get("image", ""))]
    logger.info(f"Produtos com thumbnail errado/vazio: {len(wrong_thumb)}")
    logger.info(f"Produtos com image errado/vazio: {len(wrong_image)}")

    # Fazer backup
    os.makedirs(os.path.dirname(BACKUP_FILE), exist_ok=True)
    shutil.copy2(DATABASE_FILE, BACKUP_FILE)
    logger.info(f"Backup criado: {BACKUP_FILE}")

    # Corrigir imagens
    products, fixed_ids, no_image_ids = fix_product_images(products)

    # Salvar banco corrigido
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    # Relatório
    logger.info(f"\n=== RELATÓRIO DE CORREÇÃO ===")
    logger.info(f"Produtos corrigidos: {len(fixed_ids)}")
    logger.info(f"Produtos sem imagem válida: {len(no_image_ids)}")
    if no_image_ids:
        logger.warning(f"IDs sem imagem: {no_image_ids}")

    # Diagnóstico pós-correção
    with open(DATABASE_FILE, "r", encoding="utf-8") as f:
        products_after = json.load(f)

    wrong_thumb_after = [p for p in products_after if is_wrong_image(p.get("thumbnail", ""))]
    wrong_image_after = [p for p in products_after if is_wrong_image(p.get("image", ""))]
    logger.info(f"\nPós-correção:")
    logger.info(f"  Thumbnails errados restantes: {len(wrong_thumb_after)}")
    logger.info(f"  Images erradas restantes: {len(wrong_image_after)}")

    # Salvar relatório JSON
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_products": len(products),
        "fixed": len(fixed_ids),
        "no_image": len(no_image_ids),
        "fixed_ids": fixed_ids,
        "no_image_ids": no_image_ids,
        "remaining_wrong_thumbnails": len(wrong_thumb_after),
        "remaining_wrong_images": len(wrong_image_after),
    }
    os.makedirs("data", exist_ok=True)
    with open("data/fix_images_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    logger.info(f"\nRelatório salvo em: data/fix_images_report.json")
    logger.info("=== Correção concluída ===")


if __name__ == "__main__":
    main()
