import os
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Configurações
ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = ROOT / "logs/resilience.log"
HEALTH_FILE = ROOT / "data/health/status.json"
MAX_INACTIVITY_HOURS = 2

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(LOG_FILE.parent, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def check_last_execution():
    """Verifica quanto tempo faz desde a última execução bem-sucedida."""
    if not HEALTH_FILE.exists():
        return None
    
    try:
        with open(HEALTH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            last_ts = data.get("timestamp")
            if last_ts:
                return datetime.fromisoformat(last_ts)
    except Exception as e:
        log_event(f"Erro ao ler arquivo de saúde: {e}")
    return None

def trigger_emergency_run():
    """Tenta disparar o pipeline manualmente se o cron falhar."""
    log_event("🚨 ALERTA: Inatividade detectada! Iniciando execução de emergência...")
    try:
        # Executa o orquestrador principal
        result = subprocess.run(
            ["bash", str(ROOT / "run_bot_24_7.sh")],
            capture_output=True, text=True, timeout=600
        )
        if result.returncode == 0:
            log_event("✅ Execução de emergência concluída com sucesso.")
            return True
        else:
            log_event(f"❌ Falha na execução de emergência: {result.stderr}")
            return False
    except Exception as e:
        log_event(f"❌ Erro crítico no gatilho de emergência: {e}")
        return False

def main():
    log_event("🛡️ Resilience Guard ativado.")
    last_run = check_last_execution()
    
    if last_run:
        diff = datetime.now() - last_run
        hours = diff.total_seconds() / 3600
        log_event(f"Última execução registrada há {hours:.2f} horas.")
        
        if hours > MAX_INACTIVITY_HOURS:
            trigger_emergency_run()
        else:
            log_event("🟢 Sistema dentro da janela de atividade normal.")
    else:
        log_event("⚠️ Nenhum registro de execução anterior encontrado. Iniciando primeira corrida...")
        trigger_emergency_run()

if __name__ == "__main__":
    main()
