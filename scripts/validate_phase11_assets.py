#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

PHASE11_PAGES = [
    'imprensa/index.html',
    'parcerias/index.html',
    'midia-kit/index.html',
    'precos-index/index.html',
    'academia/index.html',
    'exclusivos/index.html',
    'inteligencia/index.html',
    'pro/index.html',
    'newsletter/index.html',
]

PHASE11_DATA = [
    'data/precos-index.json',
    'data/market-intelligence.json',
    'data/revenue-metrics.json',
    'data/segmented-newsletter.json',
    'data/editorial-automation.json',
]

def validate_pages():
    """Valida se todas as páginas existem e contêm os scripts necessários"""
    print("✓ Validando páginas HTML da Fase 11...")
    missing = []
    for page in PHASE11_PAGES:
        path = ROOT / page
        if not path.exists():
            missing.append(page)
        else:
            content = path.read_text(encoding='utf-8')
            if 'compara-auth.js' not in content:
                print(f"  ⚠ {page}: Falta script compara-auth.js")
            if 'pwa.js' not in content:
                print(f"  ⚠ {page}: Falta script pwa.js")
    
    if missing:
        print(f"  ✗ Páginas faltando: {', '.join(missing)}")
        return False
    else:
        print(f"  ✓ Todas as {len(PHASE11_PAGES)} páginas encontradas e validadas")
        return True

def validate_data():
    """Valida se todos os arquivos de dados existem e são JSON válido"""
    print("\n✓ Validando arquivos de dados da Fase 11...")
    missing = []
    invalid = []
    for data_file in PHASE11_DATA:
        path = ROOT / data_file
        if not path.exists():
            missing.append(data_file)
        else:
            try:
                json.loads(path.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                invalid.append(data_file)
    
    if missing:
        print(f"  ✗ Arquivos faltando: {', '.join(missing)}")
    if invalid:
        print(f"  ✗ Arquivos JSON inválidos: {', '.join(invalid)}")
    
    if not missing and not invalid:
        print(f"  ✓ Todos os {len(PHASE11_DATA)} arquivos de dados validados")
        return True
    return False

def validate_css():
    """Valida se o CSS contém as novas classes"""
    print("\n✓ Validando CSS da Fase 11...")
    css_path = ROOT / 'assets/css/style.css'
    content = css_path.read_text(encoding='utf-8')
    
    required_classes = [
        '.precos-index-grid',
        '.feature-card',
        '.newsletter-segment-card',
        '.content-section',
        '.hero-small'
    ]
    
    missing_classes = [cls for cls in required_classes if cls not in content]
    
    if missing_classes:
        print(f"  ✗ Classes CSS faltando: {', '.join(missing_classes)}")
        return False
    else:
        print(f"  ✓ Todas as classes CSS encontradas")
        return True

def validate_service_worker():
    """Valida se o service worker inclui os novos assets"""
    print("\n✓ Validando Service Worker...")
    sw_path = ROOT / 'sw.js'
    content = sw_path.read_text(encoding='utf-8')
    
    required_assets = [
        'pro/',
        'academia/',
        'inteligencia/',
        'newsletter/',
        'precos-index.json',
        'market-intelligence.json'
    ]
    
    missing_assets = [asset for asset in required_assets if asset not in content]
    
    if missing_assets:
        print(f"  ✗ Assets faltando no SW: {', '.join(missing_assets)}")
        return False
    else:
        print(f"  ✓ Service Worker contém todos os novos assets")
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("VALIDAÇÃO FASE 11 — RADAR PRO")
    print("=" * 60)
    
    results = [
        validate_pages(),
        validate_data(),
        validate_css(),
        validate_service_worker()
    ]
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ VALIDAÇÃO COMPLETA: Todas as verificações passaram!")
    else:
        print("✗ VALIDAÇÃO COM AVISOS: Verifique os itens acima")
    print("=" * 60)
