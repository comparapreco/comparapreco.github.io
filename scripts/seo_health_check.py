import os
import sys
from bs4 import BeautifulSoup
from logger import logger

def validate_seo(file_path):
    if not os.path.exists(file_path):
        return False, "Arquivo não encontrado"
    
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    errors = []
    # 1. Title
    if not soup.title or len(soup.title.string.strip()) < 10:
        errors.append("Title ausente ou muito curto")
    
    # 2. Meta Description
    desc = soup.find("meta", attrs={"name": "description"})
    if not desc or len(desc.get("content", "").strip()) < 50:
        errors.append("Meta description ausente ou muito curta")
    
    # 3. Canonical
    if not soup.find("link", rel="canonical"):
        errors.append("Link canonical ausente")
    
    # 4. Open Graph Image
    og_img = soup.find("meta", property="og:image")
    if not og_img:
        errors.append("og:image ausente")
    
    # 5. Schema.org (JSON-LD)
    if not soup.find("script", type="application/ld+json"):
        errors.append("Schema JSON-LD ausente")
        
    if errors:
        return False, "; ".join(errors)
    return True, "SEO OK"

if __name__ == "__main__":
    # Exemplo de uso para validar a home
    success, msg = validate_seo("index.html")
    if success:
        logger.info(f"SEO Health Check: {msg}")
    else:
        logger.warning(f"SEO Health Check FAIL: {msg}")
