#!/bin/bash

# Script de entrada para execução 24/7 do Compara Preço
# Este script deve ser agendado no Crontab ou Manus Schedule

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Trava de segurança para evitar sobreposição
LOCKFILE="/tmp/radar_ninja.lock"
if [ -f "$LOCKFILE" ]; then
    echo "[$(date)] ⚠️ Já existe uma execução em curso. Abortando." >> logs/execution.log
    exit 1
fi
touch "$LOCKFILE"
trap "rm -f $LOCKFILE" EXIT

# Garantir que as pastas necessárias existam
mkdir -p logs
mkdir -p data/database

# Log de início
echo "[$(date)] 🚀 Iniciando ciclo de atualização 24/7..." >> logs/execution.log

# Executar o orquestrador resiliente
python3 scripts/self_healing.py >> logs/execution.log 2>&1
SELF_HEALING_STATUS=$?

if [ $SELF_HEALING_STATUS -ne 0 ]; then
    echo "[$(date)] ❌ Falha no ciclo. Verifique os logs detalhados." >> logs/execution.log
    exit $SELF_HEALING_STATUS
fi

# Barreiras de qualidade antes da publicação: remove duplicidades,
# valida preço/imagem/link e regenera páginas com Schema.org consistente.
python3 scripts/dedupe_products.py >> logs/execution.log 2>&1
python3 scripts/validate_products.py >> logs/execution.log 2>&1
python3 scripts/generate_pages.py >> logs/execution.log 2>&1
python3 scripts/generate_rankings.py >> logs/execution.log 2>&1
python3 scripts/generate_sitemaps.py >> logs/execution.log 2>&1
python3 scripts/generate_feeds.py >> logs/execution.log 2>&1
python3 scripts/prepublish_quality_gate.py >> logs/execution.log 2>&1
QUALITY_STATUS=$?

# Verificar status da execução
if [ $QUALITY_STATUS -eq 0 ]; then
    echo "[$(date)] ✅ Ciclo concluído com sucesso e aprovado na barreira de qualidade." >> logs/execution.log
else
    echo "[$(date)] ❌ Publicação bloqueada pela barreira de qualidade. Verifique os logs detalhados." >> logs/execution.log
    exit $QUALITY_STATUS
fi

# Limpeza de logs antigos (manter apenas os últimos 1000 linhas para economizar espaço)
tail -n 1000 logs/execution.log > logs/execution.log.tmp && mv logs/execution.log.tmp logs/execution.log
