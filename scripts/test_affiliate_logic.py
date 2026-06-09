import json
import os
from affiliate_links import build_affiliate_url

def test():
    test_product = {
        "id": "MLB123456",
        "name": "Produto Teste",
        "permalink": "https://www.mercadolivre.com.br/produto-teste-legal"
    }
    
    aff_url = build_affiliate_url(test_product)
    print(f"URL Original: {test_product['permalink']}")
    print(f"URL Afiliado: {aff_url}")
    
    if "matt_tool=60566305" in aff_url:
        print("✅ Link de afiliado gerado corretamente com matt_tool!")
    else:
        print("❌ Falha na geração do link de afiliado.")

if __name__ == "__main__":
    test()
