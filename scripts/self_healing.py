import os
import sys
import json
import subprocess
import time
from datetime import datetime
from logger import logger
from operational_utils import run_backup, send_alert

DEFAULT_TIMEOUT = 300
MAX_RETRIES = 2

def run_script_protected(script, timeout=DEFAULT_TIMEOUT):
    try:
        logger.info(f"🚀 Iniciando {script}...")
        result = subprocess.run(
            [sys.executable, f"scripts/{script}"],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stderr or result.stdout
    except Exception as e:
        return False, str(e)

def run_pipeline():
    # Pipeline completo com travas de segurança
    scripts = [
        "fetch_products_realtime.py",
        "score_products.py",
        "affiliate_links.py",
        "validate_products.py", 
        "deduplicate.py", 
        "sync_database.py",
        "editorial_automation.py", 
        "generate_blog_posts.py",
        "generate_pages.py",
        "build_categories.py",
        "build_homepage.py", 
        "generate_hubs.py",
        "build_sitemap.py",
        "seo_health_check.py",
        "health_monitor.py"
    ]
    
    essential = ["score_products.py", "sync_database.py", "generate_pages.py", "build_homepage.py"]
    
    # Snapshot inicial para validação
    db_path = "data/database/all_products.json"
    home_path = "index.html"
    initial_db_time = os.path.getmtime(db_path) if os.path.exists(db_path) else 0
    initial_home_time = os.path.getmtime(home_path) if os.path.exists(home_path) else 0
    
    for script in scripts:
        success = False
        for attempt in range(MAX_RETRIES + 1):
            success, error = run_script_protected(script)
            if success: break
            logger.warning(f"⚠️ Tentativa {attempt+1} falhou para {script}")
        
        if not success:
            send_alert(f"Falha no script {script}: {error[:200]}", "Pipeline Error")
            if script in essential:
                logger.error(f"❌ ABORTANDO: {script} falhou.")
                return False
    
    # ASSERTIONS DE PUBLICAÇÃO
    final_db_time = os.path.getmtime(db_path) if os.path.exists(db_path) else 0
    final_home_time = os.path.getmtime(home_path) if os.path.exists(home_path) else 0
    
    # 1. Validar que o banco foi atualizado
    if final_db_time == 0:
        logger.error("❌ ASSERTION FAIL: Banco de dados não encontrado.")
        return False
        
    # 2. Validar que a home foi regerada
    if final_home_time <= initial_home_time:
        logger.error("❌ ASSERTION FAIL: Home não foi regerada neste ciclo.")
        return False
        
    # 3. Validar que existem páginas de oferta
    if not os.path.exists("ofertas") or len(os.listdir("ofertas")) == 0:
        logger.error("❌ ASSERTION FAIL: Pasta de ofertas vazia ou ausente.")
        return False

    logger.info("✅ ASSERTIONS PASS: Banco e Site atualizados com sucesso.")
    run_backup()
    
    # Gerar relatório de execução
    try:
        subprocess.run([sys.executable, "scripts/execution_reporter.py"])
    except:
        pass
        
    return True

if __name__ == "__main__":
    logger.info("=== RADAR NINJA ENTERPRISE EDITION (PUBLISH-GUARD) ===")
    if run_pipeline():
        logger.info("✅ Ciclo completo concluído!")
    else:
        sys.exit(1)
