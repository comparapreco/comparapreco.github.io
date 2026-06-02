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

def run_portal_generation():
    print(f"\n🚀 Iniciando geração centralizada do Portal Radar Ninja")
    
    scripts_to_run = [
        "generate_blog_posts.py",
        "generate_programmatic_seo.py",
        "build_hubs.py",
        "apply_breadcrumbs.py",
        "smart_interlinking.py",
        "build_eeat_pages.py",
        "build_stats_center.py",
        "build_alerts.py",
        "opportunity_engine.py",
        "seo_dashboard.py",
        "generate_pages_enhanced.py",
        "build_homepage.py",
        "generate_sitemaps.py",
        "executive_report.py"
    ]
    
    for script in scripts_to_run:
        script_path = ROOT / "scripts" / script
        if not script_path.exists():
            print(f"⚠️ Script não encontrado: {script}")
            continue
            
        print(f"  - Executando {script}...")
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=600
            )
            if result.returncode != 0:
                print(f"  ❌ Erro em {script}: {result.stderr[:200]}")
            else:
                print(f"  ✅ {script} concluído.")
        except Exception as e:
            print(f"  ❌ Falha crítica em {script}: {str(e)}")

def main():
    run_portal_generation()

if __name__ == "__main__":
    main()
