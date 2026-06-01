import json
import os
from logger import logger

def validate_product(p):
    """Valida se o produto tem dados mínimos e sãos para exibição."""
    try:
        # Campos obrigatórios
        if not p.get('id') or not p.get('name') or not p.get('price'):
            return False
            
        # Validação de Preço (Evitar erros de 0 ou negativos)
        price = float(p['price'])
        if price <= 0:
            return False
            
        # Validação de URL (Mínimo de sanidade)
        url = p.get('custom_affiliate_url') or p.get('permalink')
        if not url or not url.startswith('http'):
            return False
            
        # Validação de Desconto (Evitar erros de cálculo bizarros)
        discount = p.get('custom_discount_pct', 0)
        if discount < 0 or discount > 99:
            p['custom_discount_pct'] = 0 # Resetar se for absurdo
            
        return True
    except:
        return False

def main():
    input_file = "data/new_offers.json"
    if not os.path.exists(input_file):
        logger.error("Arquivo de ofertas não encontrado para validação.")
        return

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        valid_products = [p for p in data if validate_product(p)]
        
        # Só salvar se houver uma quantidade mínima de produtos (ex: 5)
        # para evitar limpar o site inteiro por erro da API do ML
        if len(valid_products) < 5 and len(data) > 10:
            logger.error("⚠️ Alerta de Sanidade: Muitos produtos foram invalidados. Abortando para proteger o site.")
            exit(1)

        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(valid_products, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Validação concluída: {len(valid_products)} produtos aprovados.")
        
    except Exception as e:
        logger.error(f"Erro na validação de dados: {e}")
        exit(1)

if __name__ == "__main__":
    main()
