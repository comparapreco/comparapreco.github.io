import json
import os
from datetime import datetime

RAW_FILE = "data/raw_products.json"
HISTORY_FILE = "data/published_history.json"

def simulate():
    # Dados reais extraídos do browser anteriormente
    simulated_products = [
        {
            "id": "MLB65030699",
            "name": "Notebook Gamer Asus Tuf Gaming A15, Amd Ryzen 7, Rtx 3050, 8gb Ram, 512gb Ssd",
            "price": 4540.0,
            "original_price": 5469.0,
            "permalink": "https://www.mercadolivre.com.br/notebook-gamer-asus-tuf-gaming-a15-amd-ryzen-7-rtx-3050-8gb-ram-512gb-ssd-linux-keepos-graphite-black-fa506ncg-hn216/p/MLB65030699",
            "image": "https://http2.mlstatic.com/D_Q_NP_2X_630514-MLA105459813396_012026-AB.webp",
            "custom_category_slug": "informatica",
            "custom_discount_pct": 16,
            "status": "active",
            "data_coleta": datetime.now().isoformat()
        },
        {
            "id": "MLB49089309",
            "name": "Notebook Asus Vivobook 15 M1502, Amd Ryzen 7, 8 Gb Ram, 512 Gb Ssd",
            "price": 2847.0,
            "original_price": 3499.0,
            "permalink": "https://www.mercadolivre.com.br/notebook-asus-vivobook-15-m1502-amd-ryzen-7-8-gb-ram-512-gb-ssd-keepos-linux-cool-silver-m1502ya-nj611/p/MLB49089309",
            "image": "https://http2.mlstatic.com/D_Q_NP_2X_630514-MLA105459813396_012026-AB.webp",
            "custom_category_slug": "informatica",
            "custom_discount_pct": 18,
            "status": "active",
            "data_coleta": datetime.now().isoformat()
        },
        {
            "id": "MLB54963045",
            "name": "Celular Samsung Galaxy A07 256gb, 8gb, Câmera 50mp, Tela 6.7",
            "price": 1299.0,
            "original_price": 1999.0,
            "permalink": "https://www.mercadolivre.com.br/celular-samsung-galaxy-a07-256gb-8gb-camera-50mp-tela-67-protecao-ip54-processador-6nm-preto/p/MLB54963045",
            "image": "https://http2.mlstatic.com/D_Q_NP_2X_630514-MLA105459813396_012026-AB.webp",
            "custom_category_slug": "celulares",
            "custom_discount_pct": 35,
            "status": "active",
            "data_coleta": datetime.now().isoformat()
        }
    ]
    
    # Carrega histórico para ver quem é novo
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    else:
        history = {"published_ids": [], "price_history": {}}
        
    published_ids = set(history.get("published_ids", []))
    
    new_found = []
    new_count = 0
    dup_count = 0
    
    for p in simulated_products:
        if p["id"] not in published_ids:
            new_found.append(p)
            new_count += 1
            history["published_ids"].append(p["id"])
            history["price_history"][p["id"]] = p["price"]
        else:
            dup_count += 1
            
    with open(RAW_FILE, "w", encoding="utf-8") as f:
        json.dump(new_found, f, ensure_ascii=False, indent=2)
        
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
        
    print(f"Simulação concluída: {new_count} novos, {dup_count} duplicados.")

if __name__ == "__main__":
    simulate()
