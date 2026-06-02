import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from logger import logger

ROOT = Path(__file__).resolve().parents[1]

def check_bot_health():
    """Verifica se o robô está saudável e os dados estão atualizados."""
    DB_PATH = ROOT / "data/database/all_products.json"
    RAW_PATH = ROOT / "data/raw_products.json"
    
    health_report = {
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "issues": [],
        "audit": []
    }
    
    # 1. Verificar se o banco de dados existe e é recente
    if not DB_PATH.exists():
        health_report["status"] = "CRITICAL"
        health_report["issues"].append("Banco de dados ausente.")
    else:
        mtime = os.path.getmtime(DB_PATH)
        last_update = datetime.fromtimestamp(mtime)
        if datetime.now() - last_update > timedelta(hours=6):
            health_report["status"] = "WARNING"
            health_report["issues"].append(f"Dados desatualizados. Última atualização: {last_update}")

    # 2. Auditoria de Fluxo (Captura -> Publicação)
    if RAW_PATH.exists():
        try:
            with open(RAW_PATH, 'r', encoding='utf-8') as f:
                raw_products = json.load(f)
            with open(DB_PATH, 'r', encoding='utf-8') as f:
                db_products = json.load(f)
            
            db_ids = {p.get("id") for p in db_products}
            
            for p in raw_products[:10]: # Auditar os 10 mais recentes
                pid = p.get("id")
                name = p.get("name", "Sem nome")
                cat = p.get("custom_category_slug", "outros")
                
                html_exists = len(list(ROOT.glob(f"ofertas/{cat}/*{pid}.html"))) > 0
                
                audit_entry = {
                    "id": pid,
                    "name": name,
                    "captured": True,
                    "processed": pid in db_ids,
                    "published": html_exists
                }
                health_report["audit"].append(audit_entry)
                
                if not audit_entry["processed"] or not audit_entry["published"]:
                    health_report["status"] = "WARNING"
                    health_report["issues"].append(f"Produto {pid} capturado mas não publicado totalmente.")
        except Exception as e:
            health_report["issues"].append(f"Erro na auditoria de fluxo: {str(e)}")

    # Salvar relatório de saúde
    os.makedirs(ROOT / "data/health", exist_ok=True)
    with open(ROOT / "data/health/status.json", "w", encoding="utf-8") as f:
        json.dump(health_report, f, indent=2)
    
    if health_report["status"] != "OK":
        logger.error(f"🆘 ALERTA DE SAÚDE: {', '.join(health_report['issues'])}")
    else:
        logger.info("💚 Sistema operando normalmente.")

if __name__ == "__main__":
    check_bot_health()
