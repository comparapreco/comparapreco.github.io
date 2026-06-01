import os
import json
import shutil
from datetime import datetime
from logger import logger

def backup_file(file_path):
    """Cria um backup do arquivo se ele for um JSON válido."""
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f) # Validar se é JSON íntegro
        
        backup_path = f"{file_path}.bak"
        shutil.copy2(file_path, backup_path)
        return True
    except Exception as e:
        logger.error(f"Falha ao criar backup de {file_path}: {e}")
        return False

def recover_file(file_path):
    """Tenta recuperar um arquivo a partir do seu backup."""
    backup_path = f"{file_path}.bak"
    if os.path.exists(backup_path):
        logger.warning(f"Recuperando {file_path} a partir do backup...")
        shutil.copy2(backup_path, file_path)
        return True
    return False

def safe_load_json(file_path, default=[]):
    """Carrega um JSON com segurança, tentando o backup se falhar."""
    if not os.path.exists(file_path):
        if recover_file(file_path):
            pass
        else:
            return default

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Arquivo {file_path} corrompido: {e}")
        if recover_file(file_path):
            return safe_load_json(file_path, default)
        return default

def safe_save_json(file_path, data):
    """Salva um JSON criando um backup prévio."""
    if os.path.exists(file_path):
        backup_file(file_path)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar {file_path}: {e}")
        recover_file(file_path) # Tentar restaurar se o save falhou no meio
        return False
