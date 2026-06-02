import os
import sys
import json
import subprocess
import time
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
    # Pipeline atualizado com camada de qualidade
    scripts = [
        "fetch_products_realtime.py", 
        "score_products.py",         # Camada de Qualidade (Quality Score, Price Anomaly)
        "affiliate_links.py",
        "validate_products.py", 
        "deduplicate.py", 
        "sync_database.py",
        "editorial_automation.py", 
        "generate_blog_posts.py",
        "build_homepage.py",         # Diversidade por marca
        "generate_sitemaps.py",      # Sitemaps separados
        "seo_health_check.py",       # SEO Check
        "health_monitor.py"
    ]
    
    essential = ["fetch_products_realtime.py", "score_products.py", "sync_database.py", "build_homepage.py"]
    
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
    
    # Backup após sucesso
    run_backup()
    return True

if __name__ == "__main__":
    logger.info("=== RADAR NINJA ENTERPRISE EDITION ===")
    if run_pipeline():
        logger.info("✅ Pipeline concluído com sucesso!")
    else:
        sys.exit(1)
