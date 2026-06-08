import os
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE_FILE = ROOT / "data/database/all_products.json"

def create_redirect_page(old_path, new_target_url):
    """Cria uma página HTML que redireciona para o novo alvo."""
    full_old_path = ROOT / old_path
    full_old_path.parent.mkdir(parents=True, exist_ok=True)
    
    redirect_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirecionando...</title>
    <link rel="canonical" href="{new_target_url}">
    <meta http-equiv="refresh" content="0; url={new_target_url}">
    <script>window.location.href = "{new_target_url}";</script>
</head>
<body>
    <p>Página movida. Redirecionando para <a href="{new_target_url}">{new_target_url}</a>...</p>
</body>
</html>"""
    
    full_old_path.write_text(redirect_html, encoding="utf-8")

def fix_all():
    if not DATABASE_FILE.exists():
        print("Erro: Banco de dados não encontrado.")
        return

    with open(DATABASE_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"Iniciando blindagem contra 404 para {len(products)} produtos...")
    
    # Importar utilitários
    import sys
    sys.path.append(str(ROOT / "scripts"))
    from quality_utils import slugify, clean_product_name

    redirects_created = 0
    
    for p in products:
        p_id = str(p.get("id"))
        p_name = clean_product_name(p.get("name") or p.get("title"))
        p_cat = p.get("custom_category_slug", "outros")
        
        # 1. Encontrar o arquivo REAL no disco
        real_files = list(ROOT.rglob(f"*{p_id}.html"))
        if not real_files:
            continue
            
        # Pegar o arquivo de oferta mais provável (dentro da pasta ofertas)
        target_file = None
        for rf in real_files:
            if "ofertas" in rf.parts:
                target_file = rf
                break
        
        if not target_file:
            target_file = real_files[0]
            
        target_rel_url = "/" + target_file.relative_to(ROOT).as_posix()
        
        # 2. Variações de Slugs que podem causar 404
        # A) Slug com limite de 90 (antigo)
        slug_90 = slugify(p_name, max_len=90)
        path_90 = f"ofertas/{p_cat}/{slug_90}-{p_id}.html"
        
        # B) Slug enviado pelo usuário (exemplo do controle PS4)
        # O link do usuário tem um slug específico
        user_slug_example = "controle-sem-fio-joystick-bluetooth-para-ps4-videogame-tv-samsung-pc-p4-ps-4-dual-shock-manete-pc-gamer-tv-smart"
        if p_id == "MLB39960346":
            path_user = f"ofertas/celulares/{user_slug_example}-{p_id}.html"
            if (ROOT / path_user).as_posix() != target_file.as_posix():
                create_redirect_page(path_user, target_rel_url)
                redirects_created += 1

        # Criar redirecionamento se o caminho de 90 for diferente do atual
        if (ROOT / path_90).as_posix() != target_file.as_posix():
            create_redirect_page(path_90, target_rel_url)
            redirects_created += 1

    print(f"Blindagem concluída. {redirects_created} redirecionamentos criados.")

if __name__ == "__main__":
    fix_all()
