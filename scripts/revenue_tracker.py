import json
import os
from pathlib import Path
from datetime import datetime
from logger import logger

ROOT = Path(__file__).resolve().parents[1]

def track_revenue():
    logger.info("Processando dados de Monetização e Receita...")
    
    # No mundo real, aqui processaríamos logs de cliques ou API de afiliados
    # Criamos um arquivo de simulação de cliques se não existir
    click_data_file = ROOT / "data" / "click_data.json"
    if not click_data_file.exists():
        # Simulação inicial: alguns produtos populares recebem cliques
        with open(ROOT / "data" / "database" / "all_products.json", 'r') as f:
            products = json.load(f)
        initial_clicks = {p["id"]: {"clicks": 0, "name": p["name"], "category": p.get("custom_category_slug")} for p in products[:50]}
        with open(click_data_file, 'w') as f: json.dump(initial_clicks, f, indent=2)

    with open(click_data_file, 'r') as f:
        clicks = json.load(f)
        
    # Calcular estatísticas de receita
    total_clicks = sum(c["clicks"] for c in clicks.values())
    top_products = sorted(clicks.values(), key=lambda x: x["clicks"], reverse=True)[:10]
    
    revenue_stats = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_clicks": total_clicks,
        "top_performing_products": top_products,
        "revenue_estimate": total_clicks * 0.50 # Estimativa conservadora de R$ 0,50 por clique/conversão
    }
    
    with open(ROOT / "data" / "revenue_stats.json", 'w') as f:
        json.dump(revenue_stats, f, indent=2)
    logger.info(f"Dashboard de Receita atualizado: {total_clicks} cliques totais.")

if __name__ == "__main__":
    track_revenue()
