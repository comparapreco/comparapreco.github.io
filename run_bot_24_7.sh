#!/bin/bash

# Script de entrada para execução 24/7 do Compara Preço
# Este script deve ser agendado no Crontab ou Manus Schedule

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Garantir que as pastas necessárias existam
mkdir -p logs
mkdir -p data/database

# Log de início
echo "[$(date)] 🚀 Iniciando ciclo de atualização 24/7..." >> logs/execution.log

# Executar o orquestrador resiliente
python3 scripts/self_healing.py >> logs/execution.log 2>&1

# Verificar status da execução
if [ $? -eq 0 ]; then
    echo "[$(date)] ✅ Ciclo concluído com sucesso." >> logs/execution.log
else
    echo "[$(date)] ❌ Falha no ciclo. Verifique os logs detalhados." >> logs/execution.log
fi

# Limpeza de logs antigos (manter apenas os últimos 1000 linhas para economizar espaço)
tail -n 1000 logs/execution.log > logs/execution.log.tmp && mv logs/execution.log.tmp logs/execution.log
