import json
import os
from pathlib import Path
from jinja2 import Template
from logger import logger

ROOT = Path(__file__).resolve().parents[1]

def build_command_center():
    logger.info("Consolidando Centro de Comando Radar Ninja...")
    
    try:
        with open(ROOT / "data" / "index_stats.json", 'r') as f: index = json.load(f)
        with open(ROOT / "data" / "quality_audit.json", 'r') as f: quality = json.load(f)
        with open(ROOT / "data" / "revenue_stats.json", 'r') as f: revenue = json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar dados para o Centro de Comando: {e}")
        return

    template_str = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Command Center — Radar Ninja</title>
        <link rel="stylesheet" href="/assets/css/style.css">
        <style>
            .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 40px; }
            .stat-card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; }
            .val { font-size: 36px; font-weight: 900; color: var(--primary); }
            .label { font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: bold; }
            .section { background: white; padding: 30px; border-radius: 16px; margin-bottom: 30px; border: 1px solid #e2e8f0; }
            .progress-bar { height: 10px; background: #f1f5f9; border-radius: 5px; overflow: hidden; margin: 10px 0; }
            .progress-fill { height: 100%; background: var(--primary); }
        </style>
    </head>
    <body style="background: #f8fafc; color: #1e293b;">
        <main class="container">
            <header style="margin: 40px 0;">
                <h1 style="font-size: 32px;">🕹️ Radar Ninja Command Center</h1>
                <p>Visão Geral de Performance, Monetização e Saúde Técnica.</p>
            </header>

            <div class="grid">
                <div class="stat-card"><div class="val">{{ index.total_generated }}</div><div class="label">Total URLs</div></div>
                <div class="stat-card"><div class="val">{{ index.indexation_ratio }}%</div><div class="label">Indexação</div></div>
                <div class="stat-card"><div class="val">{{ revenue.total_clicks }}</div><div class="label">Total Cliques</div></div>
                <div class="stat-card"><div class="val">R$ {{ "%.2f"|format(revenue.revenue_estimate) }}</div><div class="label">Receita Est.</div></div>
            </div>

            <div class="section">
                <h3>💎 Qualidade e Saúde SEO</h3>
                <div class="progress-bar"><div class="progress-fill" style="width: {{ 100 - (quality.thin_content|length / index.total_generated * 100) }}%"></div></div>
                <p style="font-size: 14px;">{{ 100 - (quality.thin_content|length / index.total_generated * 100)|round(1) }}% das páginas atendem aos critérios de qualidade.</p>
                <ul style="font-size: 14px; margin-top: 15px;">
                    <li>Páginas com pouco conteúdo: <strong>{{ quality.thin_content|length }}</strong></li>
                    <li>Títulos duplicados: <strong>{{ quality.duplicate_titles|length }}</strong></li>
                </ul>
            </div>

            <div class="section">
                <h3>💰 Top Performance (Produtos)</h3>
                <table>
                    <thead><tr><th>Produto</th><th>Cliques</th><th>Categoria</th></tr></thead>
                    <tbody>
                        {% for p in revenue.top_performing_products %}
                        <tr><td>{{ p.name }}</td><td>{{ p.clicks }}</td><td>{{ p.category }}</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </main>
    </body>
    </html>
    """
    content = Template(template_str).render(index=index, quality=quality, revenue=revenue)
    (ROOT / "admin" / "command-center.html").write_text(content)
    logger.info("Centro de Comando unificado gerado com sucesso.")

if __name__ == "__main__":
    build_command_center()
