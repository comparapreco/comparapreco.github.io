import json
import os
from logger import logger
from quality_utils import as_float, has_bad_public_artifact, normalize_product

INPUT_CANDIDATES = [
    "data/new_offers.json",
    "data/affiliate_products.json",
    "data/scored_products.json",
]

BLOCKED_TERMS = {
    "capinha", "pelicula", "película", "usado", "recondicionado", "vitrine",
    "quebrado", "defeito", "ebook", "e-book", "pdf", "curso", "serviço",
    "assinatura", "conta premium", "link de acesso",
}


def _select_input_file() -> str:
    for path in INPUT_CANDIDATES:
        if os.path.exists(path):
            return path
    return INPUT_CANDIDATES[0]


def validate_product(product):
    """Valida, normaliza e protege a vitrine contra dados ruins de origem externa."""
    try:
        p = normalize_product(product)
        product.clear()
        product.update(p)

        if not p.get("id") or not p.get("name"):
            return False, "sem id ou nome"

        name_lower = p["name"].lower()
        if len(p["name"]) < 8 or any(term in name_lower for term in BLOCKED_TERMS):
            return False, "nome bloqueado ou genérico"

        if has_bad_public_artifact(p.get("name")):
            return False, "artefato técnico no nome"

        price = as_float(p.get("price"))
        if price <= 0:
            return False, "preço inválido"

        original = as_float(p.get("originalPrice") or p.get("original_price"))
        if original and original < price:
            p["originalPrice"] = price
            p["original_price"] = price
            p["custom_discount_pct"] = 0

        url = p.get("custom_affiliate_url") or p.get("permalink")
        if not url or not str(url).startswith("http"):
            return False, "url inválida"

        image = p.get("image") or p.get("thumbnail")
        if not image or "placeholder" in str(image).lower():
            return False, "imagem inválida"

        discount = int(p.get("custom_discount_pct") or 0)
        if discount < 0 or discount > 95:
            p["custom_discount_pct"] = 0

        if not p.get("custom_category_slug"):
            p["custom_category_slug"] = "outros"

        return True, "aprovado"
    except Exception as exc:
        return False, f"erro: {exc}"


def main():
    input_file = _select_input_file()
    if not os.path.exists(input_file):
        logger.error("Arquivo de ofertas não encontrado para validação.")
        return

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        valid_products = []
        rejected = {}
        for product in data:
            ok, reason = validate_product(product)
            if ok:
                valid_products.append(product)
            else:
                rejected[reason] = rejected.get(reason, 0) + 1

        if len(valid_products) < 5 and len(data) > 10:
            logger.error("⚠️ Alerta de Sanidade: Muitos produtos foram invalidados. Abortando para proteger o site.")
            logger.error(f"Rejeições: {rejected}")
            raise SystemExit(1)

        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(valid_products, f, ensure_ascii=False, indent=2)

        logger.info(f"Validação concluída em {input_file}: {len(valid_products)} aprovados, {len(data) - len(valid_products)} rejeitados. Motivos: {rejected}")
    except Exception as exc:
        logger.error(f"Erro na validação de dados: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
