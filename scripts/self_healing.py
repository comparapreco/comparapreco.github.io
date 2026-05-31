import os
import sys
import json
import subprocess
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
from logger import logger

def analyze_error(error_log):
    """Envia o log de erro para o GPT e solicita uma sugestão de correção ou diagnóstico."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not OPENAI_AVAILABLE or not api_key:
        logger.warning("Auto-cura desativada: OpenAI SDK não instalado ou chave ausente.")
        return None
        
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    Você é o engenheiro de manutenção do 'Radar de Preços', um robô em Python que coleta ofertas do Mercado Livre.
    O pipeline de automação falhou com o seguinte erro:
    
    {error_log}
    
    Analise o erro e forneça:
    1. Causa provável.
    2. Uma correção rápida (se possível em Python ou comando shell).
    3. Nível de gravidade.
    
    Responda em JSON no formato:
    {{"cause": "...", "fix_suggestion": "...", "severity": "high|medium|low", "can_auto_fix": true|false}}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Erro ao consultar GPT para auto-cura: {e}")
        return None

def run_pipeline():
    """Executa o pipeline principal e captura falhas."""
    scripts = [
        "fetch_products.py", "score_products.py", "affiliate_links.py", 
        "validate_products.py", "deduplicate.py", "sync_database.py",
        "generate_pages.py", "build_homepage.py"
    ]
    
    for script in scripts:
        logger.info(f"Executando {script}...")
        result = subprocess.run(
            [sys.executable, f"scripts/{script}"],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Falha no script {script}!")
            error_info = result.stderr or result.stdout
            print(f"DEBUG ERROR: {error_info}")
            analysis = analyze_error(error_info)
            
            if analysis:
                logger.info(f"Análise da IA: {analysis['cause']}")
                if analysis.get('can_auto_fix'):
                    logger.info(f"Tentando auto-correção sugerida: {analysis['fix_suggestion']}")
            
            return False
    return True

if __name__ == "__main__":
    success = run_pipeline()
    if not success:
        sys.exit(1)
    logger.info("Pipeline executado com sucesso total!")
