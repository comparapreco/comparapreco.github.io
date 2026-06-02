import os
import glob
from logger import logger

def clean_comparisons():
    comp_dir = "comparar"
    if not os.path.exists(comp_dir):
        logger.error("Diretório de comparativos não encontrado.")
        return

    html_files = glob.glob(f"{comp_dir}/*.html")
    logger.info(f"Total de comparativos encontrados: {len(html_files)}")

    # Dicionário para identificar duplicados por prefixo (nome do produto A vs B truncado)
    seen_prefixes = {}
    removed_count = 0

    for file_path in html_files:
        filename = os.path.basename(file_path)
        # Muitos comparativos parecem ter nomes truncados ou similares
        # Ex: asus-consola-port-til-512-gb-w-vs-...
        # Vamos pegar os primeiros 30 caracteres como prefixo de detecção
        prefix = filename[:30]
        
        if prefix in seen_prefixes:
            # Se o arquivo atual for menor (provavelmente nome mais truncado), removemos
            # Ou se já temos um, removemos o segundo
            try:
                os.remove(file_path)
                removed_count += 1
            except Exception as e:
                logger.error(f"Erro ao remover {file_path}: {e}")
        else:
            seen_prefixes[prefix] = file_path

    logger.info(f"Limpeza de comparativos concluída: {removed_count} arquivos removidos.")

if __name__ == "__main__":
    clean_comparisons()
