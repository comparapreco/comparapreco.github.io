#!/bin/bash

# Script de entrada resiliente para execução 24/7 do Compara Preço.
# Objetivos operacionais:
# 1. Nunca falhar silenciosamente no GitHub Actions.
# 2. Evitar travamento permanente por lockfile antigo.
# 3. Registrar cada etapa crítica com código de saída visível.
# 4. Manter a barreira de qualidade antes de publicar.

set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

mkdir -p logs data/database
LOG_FILE="logs/execution.log"
LOCKFILE="/tmp/radar_ninja.lock"
MAX_LOCK_AGE_SECONDS="${MAX_LOCK_AGE_SECONDS:-7200}"

log() {
    local message="$1"
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] ${message}" | tee -a "$LOG_FILE"
}

show_failure_context() {
    local exit_code="$1"
    log "ERRO: ciclo encerrado com código ${exit_code}. Últimas linhas do log:"
    tail -n 120 "$LOG_FILE" || true
}

cleanup() {
    rm -f "$LOCKFILE"
}
trap cleanup EXIT

if [ -f "$LOCKFILE" ]; then
    lock_age=$(( $(date +%s) - $(stat -c %Y "$LOCKFILE" 2>/dev/null || echo 0) ))
    if [ "$lock_age" -gt "$MAX_LOCK_AGE_SECONDS" ]; then
        log "AVISO: lockfile antigo encontrado (${lock_age}s). Removendo para destravar o robô."
        rm -f "$LOCKFILE"
    else
        log "AVISO: já existe execução em curso (${lock_age}s). Encerrando sem erro para não marcar a automação como quebrada."
        exit 0
    fi
fi

touch "$LOCKFILE"

run_step() {
    local label="$1"
    shift
    log "INÍCIO: ${label}"
    "$@" >> "$LOG_FILE" 2>&1
    local status=$?
    if [ "$status" -ne 0 ]; then
        log "FALHA: ${label} retornou código ${status}."
        show_failure_context "$status"
        return "$status"
    fi
    log "OK: ${label}"
    return 0
}

log "Iniciando ciclo de atualização 24/7 do Radar Ninja."

run_step "orquestrador resiliente" python3 scripts/self_healing.py || exit $?

# Barreiras de qualidade antes da publicação: remove duplicidades,
# valida preço/imagem/link e regenera páginas com Schema.org consistente.
run_step "deduplicação final de produtos" python3 scripts/dedupe_products.py || exit $?
run_step "validação final de produtos" python3 scripts/validate_products.py || exit $?
run_step "geração final de páginas" python3 scripts/generate_pages.py || exit $?
run_step "geração final de rankings" python3 scripts/generate_rankings.py || exit $?
run_step "geração final de sitemaps" python3 scripts/generate_sitemaps.py || exit $?
run_step "geração final de feeds" python3 scripts/generate_feeds.py || exit $?
run_step "barreira de qualidade pré-publicação" python3 scripts/prepublish_quality_gate.py || exit $?

log "Ciclo concluído com sucesso e aprovado na barreira de qualidade."

# Limpeza de logs antigos, mantendo contexto suficiente para auditoria.
tail -n 1500 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
