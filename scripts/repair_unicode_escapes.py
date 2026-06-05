from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "index.html", ROOT / "noticias", ROOT / "categorias", ROOT / "ofertas"]
REPLACEMENTS = {
    "\\u002F": "/",
    "\\u002f": "/",
    "u002f": "/",
    "U002F": "/",
}


def repair() -> int:
    changed = 0
    files = []
    for target in TARGETS:
        if target.is_file():
            files.append(target)
        elif target.exists():
            files.extend(target.rglob("*.html"))
    for path in files:
        content = path.read_text(encoding="utf-8", errors="ignore")
        updated = content
        for old, new in REPLACEMENTS.items():
            updated = updated.replace(old, new)
        if updated != content:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"Arquivos HTML com escapes Unicode reparados: {changed}")
    return changed


if __name__ == "__main__":
    repair()
