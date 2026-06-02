import os
import json
import shutil
from datetime import datetime
from logger import logger

def run_backup(db_path="data/database/all_products.json", backup_dir="data/backups"):
    """Mantém os últimos 30 bancos válidos."""
    if not os.path.exists(db_path):
        logger.error("Backup falhou: Banco de dados não encontrado.")
        return
    
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y_%m_%d_%Hh")
    backup_path = os.path.join(backup_dir, f"backup_{timestamp}.json")
    
    shutil.copy2(db_path, backup_path)
    logger.info(f"Backup realizado: {backup_path}")
    
    # Rotação: Manter apenas os últimos 30
    backups = sorted([os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith(".json")])
    if len(backups) > 30:
        for old_backup in backups[:-30]:
            os.remove(old_backup)
            logger.info(f"Backup antigo removido: {old_backup}")

def send_alert(message, subject="Radar Ninja Alert"):
    """
    Simula envio de alerta por e-mail. 
    Como estamos em ambiente sandbox, vamos logar como CRITICAL para o usuário ver.
    """
    logger.critical(f"ALERTA POR EMAIL [{subject}]: {message}")
    # Em produção aqui usaria smtplib ou uma API como SendGrid
    alert_log = "data/alerts_sent.json"
    alerts = []
    if os.path.exists(alert_log):
        with open(alert_log, "r") as f: alerts = json.load(f)
    
    alerts.append({"timestamp": datetime.now().isoformat(), "subject": subject, "message": message})
    with open(alert_log, "w") as f: json.dump(alerts[-50:], f, indent=2)

if __name__ == "__main__":
    run_backup()
    send_alert("Sistema operacional atualizado com camada enterprise.", "Status do Sistema")
