import os
import json
from typing import List, Dict, Any
from logger import logger
from quality_utils import clean_product_name, escape_attr, escape_html, money, normalize_product, slugify

BASE_URL = "https://comparapreco.github.io/"

def build_category_page(category_slug: str, products: List[Dict[str, Any]], template_path: str, output_dir: str) -> None:
    logger.info(f"Building page for category: {category_slug}")
    
    if not os.path.exists(template_path):
        logger.error(f"Template file not found: {template_path}")
        return

    with open(template_path, "r", encoding="utf-8") as file:
        template = file.read()
        
    cat_name = category_slug.replace("-", " ").title()
    
    def _offer_url(p):
        pname = clean_product_name(p.get("name") or p.get("title"))
        pcat = p.get("custom_category_slug", category_slug)
        pid = p.get("id", "product")
        pslug = slugify(pname)
        return f"../../offers/{pcat}/{pslug}-{pid}.html"

    products_html = ""
    for i, product in enumerate(products):
        product = normalize_product(product)
        pimg = product.get("image") or product.get("thumbnail")
        purl = _offer_url(product)
        
        if not pimg or not purl:
            continue

        pname = clean_product_name(product.get("name") or product.get("title"), 70)
        pdiscount = int(product.get("custom_discount_pct", 0) or 0)
        
        pbadge = ""
        if pdiscount >= 60:
            pbadge = '<span class="badge badge-best">BEST PRICE</span>'
        elif pdiscount >= 45:
            pbadge = '<span class="badge badge-down">PRICE DOWN</span>'
        elif i < 3:
            pbadge = '<span class="badge badge-today">TODAY</span>'

        pimg_esc = escape_attr(pimg)
        pname_esc = escape_attr(pname)
        pname_html = escape_html(pname)
        pprice = money(product.get("price"))
        porig = money(product.get("originalPrice") or product.get("original_price"))
        purl_esc = escape_attr(purl)
        
        products_html += f"""
        <div class="product-card">
            <span class="badge discount-badge">{pdiscount}% OFF</span>
            {pbadge}
            <div class="card-img"><img src="{pimg_esc}" alt="{pname_esc}"></div>
            <h3>{pname_html}</h3>
            <div class="price-tag" style="font-size: 20px;">{pprice} <span class="old-price" style="font-size: 14px;">{porig}</span></div>
            <a href="{purl_esc}" class="btn" style="width: 100%; text-align: center;">View</a>
        </div>
        """
        
    seo_title = f"Offers of {cat_name} with Discount"
    meta_desc = f"Compare {cat_name} prices, reviews and offers."
    canon_url = f"{BASE_URL}categories/{category_slug}/"

    page = template.replace("{{seo.title}}", seo_title)
    page = page.replace("{{meta.description}}", meta_desc)
    page = page.replace("{{canonical.url}}", canon_url)
    page = page.replace("{{category.name}}", cat_name)
    page = page.replace("{{category.slug}}", category_slug)
    page = page.replace("{{category.products}}", products_html)

    cats = ["technology", "games", "home", "appliances", "pet", "beauty", "fitness", "auto", "furniture"]
    for cat in cats:
        ph = f"{{{{cat_{cat}_active}}}}"
        active = "active" if cat == category_slug else ""
        page = page.replace(ph, active)
    
    out_path = os.path.join(output_dir, category_slug, "index.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    logger.info(f"Page created: {out_path}")

def build_all_category_pages(input_path: str, template_path: str, output_dir: str) -> None:
    logger.info(f"Building category pages from {input_path}")
    
    prods = []
    if os.path.exists(input_path):
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                prods = json.load(f)
        except Exception as e:
            logger.error(f"Error loading {input_path}: {e}")
    
    if not prods:
        return
        
    cats = {}
    brands = {}
    
    for prod in prods:
        cslug = prod.get("custom_category_slug", "other")
        if cslug not in cats:
            cats[cslug] = []
        cats[cslug].append(prod)
        
        pn = (prod.get("name") or "").lower()
        for br in ["samsung", "motorola", "lenovo", "lg", "jbl", "apple", "philco", "asus"]:
            if br in pn:
                if br not in brands:
                    brands[br] = []
                brands[br].append(prod)
                break
         
    alias = "offers" if output_dir != "offers" else None

    for slug, cp in cats.items():
        build_category_page(slug, cp, template_path, output_dir)
        if alias:
            build_category_page(slug, cp, template_path, alias)
         
    for brand, bp in brands.items():
        build_category_page(brand, bp, template_path, output_dir)
        if alias:
            build_category_page(brand, bp, template_path, alias)

if __name__ == "__main__":
    build_all_category_pages("data/database/all_products.json", "templates/category_template.html", "categories")
