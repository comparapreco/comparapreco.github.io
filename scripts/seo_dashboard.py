import json
import os
from pathlib import Path
from datetime import datetime
from logger import logger

ROOT = Path(__file__).resolve().parents[1]

def get_stats():
    stats = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_urls": 0,
        "total_products": 0,
        "total_comparisons": 0,
        "total_rankings": 0,
        "total_guides": 0,
        "total_categories": 0,
        "total_brands": 0,
        "top_drops": []
    }
    
    # Contar Produtos
    prod_file = ROOT / "data" / "database" / "all_products.json"
    if prod_file.exists():
        with open(prod_file, 'r') as f:
            products = json.load(f)
            stats["total_products"] = len(products)
            # Maiores quedas
            sorted_drops = sorted(products, key=lambda x: float(x.get("custom_discount_pct", 0)), reverse=True)
            stats["top_drops"] = [{"name": p["name"], "discount": p["custom_discount_pct"]} for p in sorted_drops[:10]]

    # Contar URLs por diretório
    stats["total_comparisons"] = len(list((ROOT / "comparar").glob("*.html")))
    stats["total_rankings"] = len(list((ROOT / "melhores-2026").glob("*.html")))
    stats["total_guides"] = len(list((ROOT / "guias").glob("*/index.html")))
    stats["total_categories"] = len(list((ROOT / "categorias").glob("*/index.html")))
    stats["total_brands"] = len(list((ROOT / "marcas").glob("*/index.html")))
    
    # Total de HTMLs
    stats["total_urls"] = len(list(ROOT.rglob("*.html")))
    
    return stats

def generate_dashboard_html(stats):
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>SEO Dashboard — Radar Ninja</title>
        <link rel="stylesheet" href="/assets/css/style.css">
        <style>
            .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
            .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 12px; border: 1px solid #eee; text-align: center; }}
            .stat-val {{ font-size: 32px; font-weight: 800; color: var(--primary); }}
            .stat-label {{ font-size: 14px; color: #666; text-transform: uppercase; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; border-bottom: 1px solid #eee; text-align: left; }}
        </style>
    </head>
    <body>
        <main class="container">
            <h1>📊 Radar Ninja Intelligence Dashboard</h1>
            <p>Última atualização: {stats['timestamp']}</p>
            
            <div class="stat-grid">
                <div class="stat-card"><div class="stat-val">{stats['total_urls']}</div><div class="stat-label">Total URLs</div></div>
                <div class="stat-card"><div class="stat-val">{stats['total_products']}</div><div class="stat-label">Produtos</div></div>
                <div class="stat-card"><div class="stat-val">{stats['total_comparisons']}</div><div class="stat-label">Comparativos</div></div>
                <div class="stat-card"><div class="stat-val">{stats['total_rankings']}</div><div class="stat-label">Rankings</div></div>
            </div>

            <h2>📉 Maiores Oportunidades (Queda de Preço)</h2>
            <table>
                <thead><tr><th>Produto</th><th>Desconto</th></tr></thead>
                <tbody>
                    {''.join([f"<tr><td>{p['name']}</td><td>{p['discount']}% OFF</td></tr>" for p in stats['top_drops']])}
                </tbody>
            </table>
        </main>
    </body>
    </html>
    """
    (ROOT / "admin" / "dashboard.html").write_text(html)
    logger.info("Dashboard SEO gerado com sucesso em /admin/dashboard.html")

if __name__ == "__main__":
    os.makedirs(ROOT / "admin", exist_ok=True)
    stats = get_stats()
    generate_dashboard_html(stats)
    # Salvar histórico para crescimento
    history_file = ROOT / "data" / "seo_history.json"
    history = []
    if history_file.exists():
        with open(history_file, 'r') as f: history = json.load(f)
    history.append(stats)
    with open(history_file, 'w') as f: json.dump(history[-30:], f, indent=2) # Manter últimos 30 dias
