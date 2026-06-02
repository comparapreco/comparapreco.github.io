import os
import sys
import json
import subprocess
import time
from logger import logger

# Configurações de Resiliência
DEFAULT_TIMEOUT = 300 # 5 minutos por script
MAX_RETRIES = 2

def run_script_protected(script, timeout=DEFAULT_TIMEOUT):
    """Executa um script com proteção de tempo e isolamento."""
    try:
        logger.info(f"🚀 Iniciando {script} (Timeout: {timeout}s)...")
        result = subprocess.run(
            [sys.executable, f"scripts/{script}"],
            capture_output=True, 
            text=True,
            timeout=timeout # Impede travamento infinito
        )
        
        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stderr or result.stdout
            
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT: O script {script} excedeu o limite de {timeout} segundos."
    except Exception as e:
        return False, f"CRITICAL ERROR: {str(e)}"

def run_pipeline():
    """Pipeline imparável com isolamento de falhas."""
    scripts = [
        "fetch_products.py", "score_products.py", "affiliate_links.py",
        "validate_products.py", "deduplicate.py", "deep_clean_duplicates.py", "clean_orphan_pages.py", "clean_duplicate_comparisons.py", "sync_database.py",
        "editorial_automation.py", "generate_blog_posts.py",
        "generate_pages.py", "build_categories.py", "build_homepage.py",
        "generate_compara_index.py", "generate_rankings.py", "generate_sitemaps.py", "generate_feeds.py",
        "generate_duplicate_report.py", # Novo: Gerar relatório de duplicados
        "health_monitor.py"
    ]
    
    failed_essential = [
        "fetch_products.py", "sync_database.py", "generate_blog_posts.py",
        "generate_pages.py", "build_categories.py", "build_homepage.py",
        "generate_sitemaps.py", "generate_feeds.py"
    ] # Scripts que não podem falhar para publicação automática
    
    for script in scripts:
        success = False
        last_error = ""
        
        for attempt in range(MAX_RETRIES + 1):
            success, last_error = run_script_protected(script)
            if success:
                break
            logger.warning(f"⚠️ Tentativa {attempt + 1} falhou para {script}. Erro: {last_error[:100]}...")
            time.sleep(5 * (attempt + 1))

        if not success:
            if script in failed_essential:
                logger.error(f"❌ FALHA CRÍTICA: {script} é essencial. Abortando pipeline.")
                return False
            else:
                logger.warning(f"⏩ PULANDO: {script} falhou mas não é essencial. Continuando...")
                continue
                
    return True

if __name__ == "__main__":
    logger.info("=== INICIANDO PIPELINE IMPARÁVEL ===")
    start_time = time.time()
    
    success = run_pipeline()
    
    duration = time.time() - start_time
    if success:
        logger.info(f"✅ Pipeline concluído com sucesso em {duration:.1f}s!")
    else:
        logger.error(f"🛑 Pipeline finalizado com erros após {duration:.1f}s.")
        sys.exit(1)
