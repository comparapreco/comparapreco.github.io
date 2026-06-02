from pathlib import Path
from jinja2 import Template
from logger import logger

ROOT = Path(__file__).resolve().parents[1]

def build_eeat():
    pages = {
        "metodologia": {
            "title": "Como avaliamos produtos",
            "content": "Nossa metodologia baseia-se em análise técnica, histórico de preços e feedback real de usuários..."
        },
        "equipe": {
            "title": "Equipe Editorial",
            "content": "Conheça os ninjas por trás das análises do Radar Ninja. Especialistas em tecnologia, casa e consumo."
        },
        "politica-atualizacao": {
            "title": "Política de Atualização",
            "content": "Nossos robôs monitoram preços 24/7 e atualizam as ofertas a cada 60 minutos."
        }
    }
    
    template_str = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>{{ title }} — Radar Ninja</title>
        <link rel="stylesheet" href="/assets/css/style.css">
    </head>
    <body>
        <header class="header"><div class="container"><a href="/" class="logo">📊 Radar Ninja</a></div></header>
        <main class="container" style="max-width:800px; padding:50px 20px;">
            <h1>{{ title }}</h1>
            <div class="content">{{ content }}</div>
        </main>
    </body>
    </html>
    """
    template = Template(template_str)
    
    for slug, data in pages.items():
        out_dir = ROOT / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(template.render(**data))
        logger.info(f"Página E-E-A-T gerada: {slug}")

if __name__ == "__main__":
    build_eeat()
