#!/usr/bin/env python3
"""
Auditoria de qualidade para Google AdSense
Verifica: conteúdo, meta tags, links, schema, acessibilidade
"""
import os
import json
import re
from pathlib import Path
from html.parser import HTMLParser

BASE_DIR = Path("/home/ubuntu/compara")
REPORT = {
    "total_pages": 0,
    "excellent": [],
    "good": [],
    "needs_improvement": [],
    "issues": []
}

class HTMLAnalyzer(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.h1_count = 0
        self.h2_count = 0
        self.word_count = 0
        self.images_without_alt = 0
        self.total_images = 0
        self.links = []
        self.has_breadcrumb = False
        self.has_schema_faq = False
        self.has_schema_article = False
        self.has_schema_product = False
        self.has_schema_breadcrumb = False
        self.font_sizes = []
        self.text = ""
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == "title":
            self.in_title = True
        elif tag == "meta" and attrs_dict.get("name") == "description":
            self.description = attrs_dict.get("content", "")
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "h2":
            self.h2_count += 1
        elif tag == "img":
            self.total_images += 1
            if not attrs_dict.get("alt"):
                self.images_without_alt += 1
        elif tag == "a":
            self.links.append(attrs_dict.get("href", ""))
        elif tag == "nav" and "breadcrumb" in attrs_dict.get("class", "").lower():
            self.has_breadcrumb = True
        elif tag == "script" and attrs_dict.get("type") == "application/ld+json":
            self.in_script = True
        elif tag == "style":
            # Parse font sizes
            for attr, val in attrs:
                if "font-size" in str(val):
                    self.font_sizes.append(val)

    def handle_data(self, data):
        if not self.in_script:
            self.text += data
            self.word_count = len(self.text.split())

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
            if "FAQPage" in self.text:
                self.has_schema_faq = True
            if "Article" in self.text:
                self.has_schema_article = True
            if "Product" in self.text:
                self.has_schema_product = True
            if "BreadcrumbList" in self.text:
                self.has_schema_breadcrumb = True

def analyze_html_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analyzer = HTMLAnalyzer()
        analyzer.feed(content)
        
        # Extract title from content
        title_match = re.search(r'<title>(.*?)</title>', content)
        analyzer.title = title_match.group(1) if title_match else ""
        
        return analyzer
    except Exception as e:
        print(f"Erro ao analisar {filepath}: {e}")
        return None

def classify_page(analyzer, filepath):
    """Classifica página como Excelente, Boa ou Precisa Melhorar"""
    issues = []
    score = 100
    
    # Verificações
    if not analyzer.title or len(analyzer.title) < 30:
        issues.append("❌ Title tag muito curto ou ausente")
        score -= 15
    elif len(analyzer.title) > 70:
        issues.append("⚠️ Title tag muito longo (>70 caracteres)")
        score -= 5
    
    if not analyzer.description or len(analyzer.description) < 100:
        issues.append("❌ Meta description muito curta ou ausente")
        score -= 15
    elif len(analyzer.description) > 160:
        issues.append("⚠️ Meta description muito longa (>160 caracteres)")
        score -= 5
    
    if analyzer.h1_count == 0:
        issues.append("❌ Falta H1 na página")
        score -= 20
    elif analyzer.h1_count > 1:
        issues.append("⚠️ Múltiplos H1 (deve ter apenas 1)")
        score -= 5
    
    if analyzer.word_count < 300:
        issues.append(f"❌ Conteúdo muito curto ({analyzer.word_count} palavras, mínimo 300)")
        score -= 25
    elif analyzer.word_count < 800 and "guias" in str(filepath):
        issues.append(f"⚠️ Guia com conteúdo curto ({analyzer.word_count} palavras, ideal 1500+)")
        score -= 15
    
    if analyzer.images_without_alt > 0:
        issues.append(f"⚠️ {analyzer.images_without_alt} imagens sem alt text")
        score -= 5 * analyzer.images_without_alt
    
    if not analyzer.has_breadcrumb:
        issues.append("⚠️ Falta breadcrumb visível")
        score -= 5
    
    if not analyzer.has_schema_breadcrumb:
        issues.append("⚠️ Falta schema BreadcrumbList")
        score -= 5
    
    # Verificar links internos
    internal_links = [l for l in analyzer.links if l and not l.startswith("http")]
    if len(internal_links) < 2 and "index.html" not in str(filepath):
        issues.append(f"⚠️ Poucos links internos ({len(internal_links)}, ideal 3+)")
        score -= 10
    
    # Classificação
    if score >= 85:
        return "✅ Excelente", issues, score
    elif score >= 70:
        return "🟡 Boa", issues, score
    else:
        return "🔴 Precisa Melhorar", issues, score

def audit_directory(directory, pattern="*.html"):
    """Audita todos os arquivos HTML em um diretório"""
    for filepath in Path(directory).rglob(pattern):
        # Ignorar assets e node_modules
        if "assets" in str(filepath) or "node_modules" in str(filepath):
            continue
        
        rel_path = filepath.relative_to(BASE_DIR)
        analyzer = analyze_html_file(filepath)
        
        if not analyzer:
            continue
        
        REPORT["total_pages"] += 1
        classification, issues, score = classify_page(analyzer, filepath)
        
        page_info = {
            "path": str(rel_path),
            "title": analyzer.title[:60],
            "words": analyzer.word_count,
            "h1": analyzer.h1_count,
            "images": analyzer.total_images,
            "images_no_alt": analyzer.images_without_alt,
            "links": len(analyzer.links),
            "internal_links": len([l for l in analyzer.links if l and not l.startswith("http")]),
            "has_breadcrumb": analyzer.has_breadcrumb,
            "has_schema": {
                "faq": analyzer.has_schema_faq,
                "article": analyzer.has_schema_article,
                "product": analyzer.has_schema_product,
                "breadcrumb": analyzer.has_schema_breadcrumb
            },
            "issues": issues,
            "score": score
        }
        
        if "Excelente" in classification:
            REPORT["excellent"].append(page_info)
        elif "Boa" in classification:
            REPORT["good"].append(page_info)
        else:
            REPORT["needs_improvement"].append(page_info)

def generate_report():
    """Gera relatório em Markdown"""
    audit_directory(BASE_DIR)
    
    report_md = "# 📊 Auditoria de Qualidade para Google AdSense\n\n"
    report_md += f"**Data:** {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    report_md += f"**Total de Páginas:** {REPORT['total_pages']}\n\n"
    
    report_md += "## 📈 Resumo\n\n"
    report_md += f"- ✅ **Excelente:** {len(REPORT['excellent'])} páginas\n"
    report_md += f"- 🟡 **Boa:** {len(REPORT['good'])} páginas\n"
    report_md += f"- 🔴 **Precisa Melhorar:** {len(REPORT['needs_improvement'])} páginas\n\n"
    
    # Páginas Excelentes
    if REPORT['excellent']:
        report_md += "## ✅ Páginas Excelentes\n\n"
        for page in sorted(REPORT['excellent'], key=lambda x: x['score'], reverse=True)[:10]:
            report_md += f"### {page['path']}\n"
            report_md += f"- **Score:** {page['score']}/100\n"
            report_md += f"- **Palavras:** {page['words']}\n"
            report_md += f"- **Links internos:** {page['internal_links']}\n\n"
    
    # Páginas Boas
    if REPORT['good']:
        report_md += "## 🟡 Páginas Boas\n\n"
        for page in sorted(REPORT['good'], key=lambda x: x['score'], reverse=True)[:10]:
            report_md += f"### {page['path']}\n"
            report_md += f"- **Score:** {page['score']}/100\n"
            report_md += f"- **Palavras:** {page['words']}\n"
            if page['issues']:
                report_md += f"- **Problemas:** {', '.join(page['issues'][:2])}\n"
            report_md += "\n"
    
    # Páginas que Precisam Melhorar
    if REPORT['needs_improvement']:
        report_md += "## 🔴 Páginas que Precisam Melhorar\n\n"
        for page in sorted(REPORT['needs_improvement'], key=lambda x: x['score'])[:15]:
            report_md += f"### {page['path']}\n"
            report_md += f"- **Score:** {page['score']}/100\n"
            report_md += f"- **Palavras:** {page['words']}\n"
            if page['issues']:
                report_md += f"- **Problemas:**\n"
                for issue in page['issues'][:3]:
                    report_md += f"  - {issue}\n"
            report_md += "\n"
    
    # Recomendações
    report_md += "## 💡 Recomendações Prioritárias\n\n"
    report_md += "1. **Expandir conteúdo:** Páginas com <800 palavras devem ser expandidas\n"
    report_md += "2. **Adicionar links internos:** Cada página deve ter 3+ links internos\n"
    report_md += "3. **Alt text em imagens:** Todas as imagens devem ter descrição\n"
    report_md += "4. **Schema markup:** Adicionar schema FAQPage, Article, Product onde aplicável\n"
    report_md += "5. **Breadcrumbs:** Garantir breadcrumbs visíveis em todas as páginas\n"
    
    # Salvar relatório
    with open(BASE_DIR / "AUDITORIA_ADSENSE.md", "w", encoding="utf-8") as f:
        f.write(report_md)
    
    print(report_md)
    print(f"\n✅ Relatório salvo em: AUDITORIA_ADSENSE.md")

if __name__ == "__main__":
    generate_report()
