import os
import json
import time
from datetime import datetime, timedelta
from logger import logger

def check_bot_health():
    """Verifica se o robô está saudável e os dados estão atualizados."""
    DB_PATH = "data/database/all_products.json"
    LOG_PATH = "logs/execution.log"
    
    health_report = {
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "issues": []
    }
    
    # 1. Verificar se o banco de dados existe e é recente
    if not os.path.exists(DB_PATH):
        health_report["status"] = "CRITICAL"
        health_report["issues"].append("Banco de dados ausente.")
    else:
        mtime = os.path.getmtime(DB_PATH)
        last_update = datetime.fromtimestamp(mtime)
        if datetime.now() - last_update > timedelta(hours=6):
            health_report["status"] = "WARNING"
            health_report["issues"].append(f"Dados desatualizados. Última atualização: {last_update}")

    # 2. Verificar integridade do JSON
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if len(data) < 5:
                health_report["status"] = "WARNING"
                health_report["issues"].append(f"Catálogo muito pequeno: apenas {len(data)} produtos.")
    except Exception as e:
        health_report["status"] = "CRITICAL"
        health_report["issues"].append(f"Erro de leitura no banco: {str(e)}")

    # Salvar relatório de saúde
    os.makedirs("data/health", exist_ok=True)
    with open("data/health/status.json", "w", encoding="utf-8") as f:
        json.dump(health_report, f, indent=2)
    
    if health_report["status"] != "OK":
        logger.error(f"🆘 ALERTA DE SAÚDE: {', '.join(health_report['issues'])}")
    else:
        logger.info("💚 Sistema operando normalmente.")

if __name__ == "__main__":
    check_bot_health()
