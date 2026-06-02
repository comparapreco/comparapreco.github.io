import json
import os
from pathlib import Path
from jinja2 import Template
from logger import logger

ROOT = Path(__file__).resolve().parents[1]

def build_control_center():
    logger.info("Construindo Centro de Controle Radar Ninja...")
    
    # Carregar todos os dados de monitoramento
    try:
        with open(ROOT / "data" / "seo_history.json", 'r') as f: history = json.load(f)
        with open(ROOT / "data" / "quality_audit.json", 'r') as f: quality = json.load(f)
        with open(ROOT / "data" / "index_stats.json", 'r') as f: index = json.load(f)
    except:
        logger.error("Dados de monitoramento incompletos.")
        return

    template_str = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Control Center — Radar Ninja</title>
        <link rel="stylesheet" href="/assets/css/style.css">
        <style>
            .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
            .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
            .status-ok { color: #22c55e; font-weight: bold; }
            .status-warn { color: #f59e0b; font-weight: bold; }
            .status-err { color: #ef4444; font-weight: bold; }
            .big-num { font-size: 48px; font-weight: 900; margin: 10px 0; }
        </style>
    </head>
    <body style="background:#f1f5f9;">
        <main class="container">
            <header style="margin-bottom:40px;">
                <h1>🛡️ Radar Ninja Control Center</h1>
                <p>Monitoramento em tempo real da saúde e performance do portal.</p>
            </header>

            <div class="dashboard-grid">
                <div class="card">
                    <h3>🚀 Crescimento</h3>
                    <div class="big-num">{{ index.total_generated }}</div>
                    <p>Total de URLs geradas</p>
                    <p class="status-ok">📈 +{{ history[-1].total_urls - history[0].total_urls if history|length > 1 else 0 }} esta semana</p>
                </div>
                
                <div class="card">
                    <h3>🔍 Indexação</h3>
                    <div class="big-num">{{ index.indexation_ratio }}%</div>
                    <p>Cobertura no Sitemap</p>
                    <p class="status-warn">URLs em Sitemap: {{ index.total_in_sitemap }}</p>
                </div>

                <div class="card">
                    <h3>💎 Qualidade SEO</h3>
                    <div class="big-num">{{ quality.thin_content|length }}</div>
                    <p>Páginas com pouco conteúdo</p>
                    <p class="{{ 'status-err' if quality.duplicate_titles|length > 0 else 'status-ok' }}">
                        Títulos Duplicados: {{ quality.duplicate_titles|length }}
                    </p>
                </div>
            </div>

            <section style="margin-top:40px;">
                <div class="card">
                    <h3>📊 Cobertura por Categoria</h3>
                    <table>
                        <thead><tr><th>Categoria</th><th>Páginas</th></tr></thead>
                        <tbody>
                            {% for cat, count in index.categories_coverage.items() %}
                            <tr><td>{{ cat|title }}</td><td>{{ count }}</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </section>
        </main>
    </body>
    </html>
    """
    content = Template(template_str).render(history=history, quality=quality, index=index)
    (ROOT / "admin" / "control-center.html").write_text(content)
    logger.info("Centro de Controle gerado em /admin/control-center.html")

if __name__ == "__main__":
    build_control_center()
