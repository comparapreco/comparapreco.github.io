import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS_FILE = ROOT / "data/cycle_metrics.json"
REPORT_FILE = ROOT / "data/health/last_execution_report.json"
MARKDOWN_REPORT = ROOT / "EXECUTION_REPORT.md"

def generate_report():
    if not METRICS_FILE.exists():
        return
    
    try:
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        
        if not metrics:
            return
            
        last_cycle = metrics[-1]
        
        report = {
            "execution_time": last_cycle.get("timestamp"),
            "products_found": last_cycle.get("produtos_processados", 0),
            "products_published": last_cycle.get("publicados", 0),
            "errors": last_cycle.get("errors", []),
            "status": "SUCCESS" if not last_cycle.get("errors") else "PARTIAL"
        }
        
        # Salvar JSON
        os.makedirs(REPORT_FILE.parent, exist_ok=True)
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
        # Gerar Markdown para fácil visualização no GitHub
        md_content = f"""# 📊 Relatório de Execução Radar Ninja

**Última Atualização:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

| Métrica | Valor |
|---------|-------|
| **Horário da Execução** | {report['execution_time']} |
| **Produtos Encontrados** | {report['products_found']} |
| **Produtos Publicados** | {report['products_published']} |
| **Status** | {report['status']} |

## 🛠️ Detalhes da Execução
- **Total Raw:** {last_cycle.get('detalhes', {}).get('total_raw', 0)}
- **Aprovados:** {last_cycle.get('detalhes', {}).get('approved', 0)}
- **Bloqueados (Qualidade):** {last_cycle.get('detalhes', {}).get('blocked_low_quality', 0)}

## ❌ Erros Encontrados
{chr(10).join([f'- {e}' for e in report['errors']]) if report['errors'] else 'Nenhum erro registrado.'}

---
*Gerado automaticamente pelo Radar Ninja Resilience Guard.*
"""
        with open(MARKDOWN_REPORT, "w", encoding="utf-8") as f:
            f.write(md_content)
            
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")

if __name__ == "__main__":
    generate_report()
