import json
import os
from pathlib import Path
from datetime import datetime
from logger import logger

ROOT = Path(__file__).resolve().parents[1]

def generate_report():
    logger.info("Gerando Relatório Executivo Semanal...")
    
    # Carregar dados atuais
    prod_file = ROOT / "data" / "database" / "all_products.json"
    with open(prod_file, 'r') as f: products = json.load(f)
    
    # Carregar histórico
    history_file = ROOT / "data" / "seo_history.json"
    history = []
    if history_file.exists():
        with open(history_file, 'r') as f: history = json.load(f)
    
    # Calcular crescimento (últimos 7 dias ou registros disponíveis)
    growth = "N/A"
    if len(history) >= 2:
        old = history[0]["total_urls"]
        new = history[-1]["total_urls"]
        diff = new - old
        growth = f"+{diff} URLs"
        
    report = f"""
    # 📊 Relatório Executivo Radar Ninja
    **Data:** {datetime.now().strftime("%Y-%m-%d")}
    
    ## 📈 Crescimento e Escala
    - **Total de Produtos Monitorados:** {len(products)}
    - **Crescimento do Período:** {growth}
    - **Total de Comparativos Gerados:** {len(list((ROOT / "comparar").glob("*.html")))}
    - **Total de Rankings Ativos:** {len(list((ROOT / "melhores-2026").glob("*.html")))}
    
    ## 🔍 Saúde do Portal
    - **Hubs de Categoria:** {len(list((ROOT / "categorias").glob("*/index.html")))}
    - **Hubs de Marca:** {len(list((ROOT / "marcas").glob("*/index.html")))}
    - **Sitemaps Ativos:** 7
    
    ## 🚀 Ações Realizadas
    - Implementação da Fase 6: Dominação SEO e Conversão.
    - Criação da Central de Estatísticas e Tendências.
    - Otimização de Breadcrumbs e Interlinking.
    - Injeção de Blocos de Conversão (Prós/Contras/Alternativas).
    
    ## 🛠 Próximos Passos
    - Refinamento do Search Experience (Busca Interna).
    - Expansão da Auto-Recuperação de Conteúdo.
    """
    
    (ROOT / "reports" / f"relatorio_executivo_{datetime.now().strftime('%Y%m%d')}.md").write_text(report)
    logger.info("Relatório Executivo gerado com sucesso.")

if __name__ == "__main__":
    os.makedirs(ROOT / "reports", exist_ok=True)
    generate_report()
