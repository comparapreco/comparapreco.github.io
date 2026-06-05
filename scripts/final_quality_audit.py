import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "health" / "final_quality_audit.json"
INTERNAL_HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.I)
BAD_RE = re.compile(r"u002f|MLB\d{5,}.*\d{14}|\d{14}", re.I)


def is_internal(href: str) -> bool:
    if href.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:")):
        return href.startswith("https://comparapreco.github.io/")
    return href.endswith(".html") or href.startswith(("/", "../", "./"))


def resolve(path: Path, href: str) -> Path | None:
    if href.startswith("https://comparapreco.github.io/"):
        href = href.replace("https://comparapreco.github.io/", "/", 1)
    href = href.split("#", 1)[0].split("?", 1)[0]
    if not href or href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:")):
        return None
    if href.startswith("/"):
        target = ROOT / href.lstrip("/")
    else:
        target = (path.parent / href).resolve()
    if href.endswith("/"):
        target = target / "index.html"
    return target


def audit():
    html_files = [ROOT / "index.html"] + [p for p in ROOT.rglob("*.html") if ".git" not in p.parts and "templates" not in p.parts and p.name != "index.html"]
    broken = []
    bad_public = []
    for path in html_files:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if BAD_RE.search(content):
            # Permitir IDs de produto em URLs limpas e imagens externas; sinalizar apenas escapes/timestamps ou títulos contaminados.
            if "u002f" in content.lower() or re.search(r"<(?:title|h1|h2|h3)[^>]*>[^<]*(?:MLB\d{5,}|\d{14})", content, re.I):
                bad_public.append(str(path.relative_to(ROOT)))
        for href in INTERNAL_HREF_RE.findall(content):
            if not is_internal(href):
                continue
            target = resolve(path, href)
            if target and not target.exists():
                broken.append({"file": str(path.relative_to(ROOT)), "href": href})
                if len(broken) >= 50:
                    break
    result = {
        "html_files_checked": len(html_files),
        "broken_internal_links": len(broken),
        "bad_public_artifact_files": len(bad_public),
        "broken_samples": broken[:20],
        "bad_public_samples": bad_public[:20],
        "status": "OK" if not broken and not bad_public else "WARN",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    audit()
