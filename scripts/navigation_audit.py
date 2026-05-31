
import os
import re

def audit_navigation():
    # 1. Mapear arquivos HTML existentes
    html_files = []
    for root, dirs, files in os.walk('.'):
        if 'node_modules' in root or root.startswith('./.'): continue
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    # 2. Ler arquivos principais para checar links
    with open('index.html', 'r') as f: index_content = f.read()
    
    explorar_path = 'templates/explorar_menu.html'
    explorar_content = ""
    if os.path.exists(explorar_path):
        with open(explorar_path, 'r') as f: explorar_content = f.read()
    
    # 3. Gerar Relatório
    report = "# 🕵️ Auditoria de Navegação - Compara Preço\n\n"
    report += "| Página | Arquivo | Menu/Footer | Explorar | Status |\n"
    report += "| :--- | :--- | :---: | :---: | :---: |\n"
    
    strategic_pages = [
        {"name": "Início", "path": "index.html", "url": "/"},
        {"name": "Blog/Notícias", "path": "noticias/index.html", "url": "noticias/"},
        {"name": "Comparar", "path": "comparar/index.html", "url": "comparar/"},
        {"name": "Marcas", "path": "marcas/index.html", "url": "marcas/"},
        {"name": "Glossário", "path": "glossario/index.html", "url": "glossario/"},
        {"name": "Alertas", "path": "alertas/index.html", "url": "alertas/"},
        {"name": "Quedas Hoje", "path": "quedas-hoje/index.html", "url": "quedas-hoje/"},
        {"name": "Vale a Pena Esperar", "path": "vale-a-pena-esperar/index.html", "url": "vale-a-pena-esperar/"},
        {"name": "Mais Clicados", "path": "mais-clicados/index.html", "url": "mais-clicados/"},
        {"name": "Calendário de Preços", "path": "calendario-de-precos/index.html", "url": "calendario-de-precos/"},
        {"name": "Melhores 2026", "path": "melhores-2026/index.html", "url": "melhores-2026/"},
        {"name": "Estatísticas", "path": "estatisticas/index.html", "url": "estatisticas/"},
        {"name": "Compara Preço de Mercado", "path": "radar-de-mercado/index.html", "url": "radar-de-mercado/"},
        {"name": "Prêmio Compara Preço 2026", "path": "premio-radar-2026/index.html", "url": "premio-radar-2026/"},
        {"name": "Simulador Economia", "path": "ferramentas/economia/index.html", "url": "ferramentas/economia/"},
        {"name": "Metodologia", "path": "metodologia/index.html", "url": "metodologia/"},
        {"name": "O Que Está em Alta", "path": "tendencias/index.html", "url": "tendencias/"},
    ]
    
    for page in strategic_pages:
        exists = os.path.exists(page['path'])
        in_menu = "Sim" if page['url'] in index_content else "Não"
        in_explorar = "Sim" if page['url'] in explorar_content else "Não"
        
        status = "✅ OK" if exists else "❌ INEXISTENTE"
        if exists and in_menu == "Não" and in_explorar == "Não": status = "⚠️ ÓRFÃ"
        
        report += f"| {page['name']} | `{page['path']}` | {in_menu} | {in_explorar} | {status} |\n"
    
    with open('AUDITORIA_NAVEGACAO.md', 'w') as f:
        f.write(report)
    print("Relatório de auditoria gerado: AUDITORIA_NAVEGACAO.md")

if __name__ == "__main__":
    audit_navigation()
