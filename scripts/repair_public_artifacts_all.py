from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def clean_segment(segment: str) -> str:
    cleaned = segment.replace("\\u002F", "-").replace("\\u002f", "-")
    cleaned = cleaned.replace("u002f", "-").replace("U002F", "-")
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or segment


def build_rename_map():
    mapping = {}
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT)
        parts = [clean_segment(part) for part in rel.parts]
        new_rel = Path(*parts)
        if new_rel != rel:
            mapping[rel.as_posix()] = new_rel.as_posix()
    return mapping


def apply_renames(mapping):
    changed = 0
    for old_rel, new_rel in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        old = ROOT / old_rel
        new = ROOT / new_rel
        if not old.exists():
            continue
        new.parent.mkdir(parents=True, exist_ok=True)
        if new.exists():
            old.unlink()
        else:
            old.rename(new)
        changed += 1
    return changed


def repair_contents(mapping):
    changed = 0
    html_files = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts]
    for path in html_files:
        content = path.read_text(encoding="utf-8", errors="ignore")
        updated = content
        # Corrigir CSS das páginas em /comparar/*.html, que ficam apenas um nível abaixo da raiz.
        if path.parent == ROOT / "comparar":
            updated = updated.replace('../../assets/', '../assets/')
        # Remover escapes legados em conteúdo visível e atributos.
        updated = updated.replace("\\u002F", "/").replace("\\u002f", "/")
        updated = updated.replace("u002f", "/").replace("U002F", "/")
        # Atualizar links relativos para arquivos renomeados.
        for old_rel, new_rel in mapping.items():
            old_name = Path(old_rel).name
            new_name = Path(new_rel).name
            updated = updated.replace(old_rel, new_rel)
            updated = updated.replace(old_name, new_name)
        if updated != content:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def main():
    mapping = build_rename_map()
    renamed = apply_renames(mapping)
    content_changed = repair_contents(mapping)
    print(f"Arquivos renomeados: {renamed}")
    print(f"Arquivos com conteúdo reparado: {content_changed}")


if __name__ == "__main__":
    main()
