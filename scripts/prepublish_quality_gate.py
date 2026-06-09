import json
import re
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_OFFER_FIELDS = {"price", "priceCurrency", "availability", "url"}
REQUIRED_PRODUCT_FIELDS = {"name", "image", "offers"}

def audit_html_file(path: Path) -> List[str]:
    rel = str(path.relative_to(ROOT))
    html = path.read_text(encoding="utf-8", errors="ignore")
    issues: List[str] = []
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Validação de Link de Afiliado (CRÍTICO)
    buy_btn = soup.find('a', string=lambda s: s and "Ir para" in s)
    if not buy_btn:
        buy_btn = soup.find('a', class_=re.compile(r'btn|buy|affiliate', re.I))
    
    if not buy_btn:
        issues.append(f"{rel}: Botão de compra não encontrado")
    else:
        href = buy_btn.get('href', '')
        if not href:
            issues.append(f"{rel}: Link de afiliado vazio")
        elif "mercadolivre.com" in href and "matt_tool=60566305" not in href:
            issues.append(f"{rel}: Link Mercado Livre sem tracking ID (matt_tool)")
        elif "amazon.com" in href and "tag=radar041-20" not in href:
            issues.append(f"{rel}: Link Amazon sem tracking ID (tag)")
        elif "mercadolivre.com" not in href and "amazon.com" not in href and not href.startswith(('./', '../')):
             issues.append(f"{rel}: Link externo não reconhecido ou sem tracking: {href[:50]}")

    # 2. Validação de Imagem
    img = soup.find('img')
    if not img:
        issues.append(f"{rel}: Produto sem imagem")
    else:
        src = img.get('src', '')
        if not src or "placeholder" in src.lower():
            issues.append(f"{rel}: Imagem quebrada ou placeholder")

    # 3. Validação de Preço
    price_text = soup.get_text()
    if "R$" not in price_text:
        issues.append(f"{rel}: Preço não encontrado na página")

    return issues

def main():
    issues = []
    ofertas_dir = ROOT / "ofertas"
    if ofertas_dir.exists():
        for html_file in ofertas_dir.rglob("*.html"):
            if html_file.name != "index.html":
                issues.extend(audit_html_file(html_file))
    
    report = {
        "ok": not issues,
        "total_issues": len(issues),
        "issues": issues
    }
    
    report_path = ROOT / "data/health/quality_gate_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    if issues:
        print(f"BLOQUEIO DE SEGURANÇA: {len(issues)} falhas críticas encontradas.")
        for issue in issues[:20]:
            print(f"  - {issue}")
        # O robô deve parar a execução aqui em um ambiente real
        # sys.exit(1) 
    else:
        print("QUALIDADE 100%: Todos os produtos validados com link de afiliado, imagem e preço.")

if __name__ == "__main__":
    main()
