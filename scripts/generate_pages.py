import os
import json
import random
from typing import List, Dict, Any
from logger import logger

BASE_URL = "https://comparadordepreco.github.io/"

def slugify(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.lower().replace(' ', '-')
    return ''.join(c for c in text if c.isalnum() or c == '-')

def generate_product_page(product: Dict[str, Any], all_products: List[Dict[str, Any]], template_path: str, output_dir: str) -> None:
    product_name = product.get('name') or product.get('title') or 'Produto'
    
    if not os.path.exists(template_path): 
        return

    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
        
    p_id = product.get('id', '0')
    p_slug = slugify(product_name)
    p_cat_slug = product.get('custom_category_slug', 'outros')
    p_status = product.get('status', 'active')
    
    # Formatação de preços
    try:
        price_val = float(product.get('price', 0))
        orig_val = float(product.get('originalPrice', 0))
    except (ValueError, TypeError):
        price_val = 0.0
        orig_val = 0.0
        
    p_price = f"R$ {price_val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    p_orig = f"R$ {orig_val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    p_img = product.get('image') or product.get('thumbnail') or ''
    
    # Lógica de URL Afiliada
    _aff = product.get('custom_affiliate_url', '')
    _is_valid_aff = _aff and '/social/' not in _aff and 'vendas0nline?' not in _aff
    p_url = _aff if _is_valid_aff else (product.get('permalink') or '')
    
    p_discount = product.get('custom_discount_pct', 0)
    
    # Lógica de Status e Similares (Fase 2)
    status_html = ""
    if p_status == 'expired':
        status_html = '<div class="status-banner expired">⚠️ Esta oferta encerrou, mas confira produtos similares abaixo!</div>'
    
    # Buscar similares da mesma categoria
    similars = [p for p in all_products if p.get('custom_category_slug') == p_cat_slug and p['id'] != p_id and p.get('status') == 'active']
    random.shuffle(similars)
    similars = similars[:4]
    
    similars_html = ""
    if similars:
        similars_html = '<div class="similar-products"><h2>Produtos Similares em Oferta</h2><div class="products-grid">'
        for s in similars:
            s_price = f"R$ {float(s.get('price', 0)):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            s_slug = slugify(s.get('name', ''))
            s_url = f"../../ofertas/{s.get('custom_category_slug', 'outros')}/{s_slug}-{s['id']}.html"
            similars_html += f"""
            <div class="product-card">
                <div class="card-img"><img src="{s.get('image', '')}" alt="{s.get('name', '')}"></div>
                <h3>{s.get('name', '')[:40]}...</h3>
                <div class="price-tag">{s_price}</div>
                <a href="{s_url}" class="btn">Ver Oferta</a>
            </div>
            """
        similars_html += '</div></div>'

    # SEO DINÂMICO
    seo_title = f"{product_name} | Compara Preço"
    if p_status == 'active':
        seo_title = f"{product_name} com {p_discount}% de Desconto | Compara Preço"
    
    meta_desc = f"Confira a oferta de {product_name} no Compara Preço. Economize com os melhores descontos do Mercado Livre."
    canonical_url = f"{BASE_URL}ofertas/{p_cat_slug}/{p_slug}-{p_id}.html"
    
    # Substituições
    content = template.replace('{{seo.title}}', seo_title)
    content = content.replace('{{meta.description}}', meta_desc)
    content = content.replace('{{canonical.url}}', canonical_url)
    content = content.replace('{{product.status_banner}}', status_html)
    content = content.replace('{{product.similars}}', similars_html)
    
    content = content.replace('{{product.name}}', product_name)
    content = content.replace('{{product.price}}', p_price)
    content = content.replace('{{product.price_raw}}', str(price_val))
    content = content.replace('{{product.originalPrice}}', p_orig)
    content = content.replace('{{product.originalPrice_raw}}', str(orig_val))
    content = content.replace('{{product.image}}', p_img)
    content = content.replace('{{product.url}}', p_url)
    content = content.replace('{{product.id}}', p_id)
    content = content.replace('{{product.category}}', p_cat_slug)
    content = content.replace('{{product.discount}}', str(p_discount))
    
    desc = product.get('description', f"Confira esta oferta de {product_name} no Mercado Livre! Produto selecionado pelo Compara Preço.")
    content = content.replace('{{product.description_content}}', desc)
    
    path = os.path.join(output_dir, p_cat_slug, f'{p_slug}-{p_id}.html')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def generate_all(input_p: str, temp_p: str, out_d: str) -> None:
    if not os.path.exists(input_p): 
        return
    try:
        with open(input_p, 'r', encoding='utf-8') as f:
            all_products = json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler banco de dados: {e}")
        return
        
    logger.info(f"Gerando {len(all_products)} páginas permanentes...")
    for p in all_products:
        generate_product_page(p, all_products, temp_p, out_d)

if __name__ == '__main__':
    # Agora gera a partir do BANCO DE DADOS COMPLETO, não apenas das novas ofertas
    generate_all('data/database/all_products.json', 'templates/product_template.html', 'ofertas')
