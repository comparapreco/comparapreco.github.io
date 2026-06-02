import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "data" / "network_config.json"

def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_site_generation(site_key, site_config):
    print(f"\n🚀 Iniciando geração para: {site_config['name']} ({site_key})")
    
    # Criar ambiente para o site (variáveis de ambiente ou argumentos)
    env = os.environ.copy()
    env["SITE_KEY"] = site_key
    env["SITE_NAME"] = site_config["name"]
    env["SITE_CATEGORIES"] = ",".join(site_config["categories"])
    env["SITE_ROOT"] = str(ROOT / "sites" / site_key)
    
    scripts_to_run = [
        "generate_blog_posts.py",
        "generate_programmatic_seo.py",
        "generate_pages_enhanced.py",
        "build_homepage.py",
        "generate_sitemaps.py"
    ]
    
    for script in scripts_to_run:
        script_path = ROOT / "scripts" / script
        if not script_path.exists():
            print(f"⚠️ Script não encontrado: {script}")
            continue
            
        print(f"  - Executando {script}...")
        try:
            # Passamos o SITE_KEY como argumento para os scripts que suportarem
            result = subprocess.run(
                [sys.executable, str(script_path), site_key],
                env=env,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode != 0:
                print(f"  ❌ Erro em {script}: {result.stderr[:200]}")
            else:
                print(f"  ✅ {script} concluído.")
        except Exception as e:
            print(f"  ❌ Falha crítica em {script}: {str(e)}")

def main():
    config = load_config()
    for site_key, site_config in config["sites"].items():
        run_site_generation(site_key, site_config)

if __name__ == "__main__":
    main()
