import re
from difflib import SequenceMatcher
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "noticias" / "index.html"
POSTS = ROOT / "noticias" / "posts"
BASE_URL = "https://comparapreco.github.io/noticias/posts/"


def extract_news_items(index_text):
    items = []
    for match in re.finditer(r'\{\s*"id"\s*:\s*.*?\n\s*\}', index_text, flags=re.S):
        block = match.group(0)
        title_m = re.search(r'"title"\s*:\s*"(.*?)"\s*,', block, flags=re.S)
        url_m = re.search(r'"url"\s*:\s*"(.*?)"', block, flags=re.S)
        if title_m and url_m:
            items.append({"title": title_m.group(1), "url": url_m.group(1)})
    return items


def normalized(value):
    value = value.lower()
    value = re.sub(r'[^a-z0-9áàâãéêíóôõúç]+', ' ', value)
    for token in ["analise", "análise", "completa", "vale", "pena", "comprar", "com", "off", "desconto", "posts", "html"]:
        value = re.sub(rf'\b{token}\b', ' ', value)
    return re.sub(r'\s+', ' ', value).strip()


def post_title(path):
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(" ", strip=True)
    title = soup.find("title")
    if title:
        return title.get_text(" ", strip=True)
    return path.stem


def build_existing_index():
    existing = []
    for path in POSTS.glob("*.html"):
        title = post_title(path)
        searchable = f"{title} {path.stem}"
        existing.append({
            "path": path,
            "url": f"posts/{path.name}",
            "title": title,
            "norm": normalized(searchable),
        })
    return existing


def choose_target(item, existing):
    query = normalized(f"{item['title']} {Path(item['url']).stem}")
    scored = sorted(
        ((SequenceMatcher(None, query, entry["norm"]).ratio(), entry) for entry in existing),
        key=lambda pair: pair[0],
        reverse=True,
    )
    score, entry = scored[0]
    return score, entry


def create_redirect(old_rel_url, target_rel_url):
    old_path = ROOT / "noticias" / old_rel_url
    old_path.parent.mkdir(parents=True, exist_ok=True)
    target_filename = Path(target_rel_url).name
    canonical = BASE_URL + target_filename
    html = f"""<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Publicação movida | Compara Preço</title>
  <link rel=\"canonical\" href=\"{canonical}\">
  <meta http-equiv=\"refresh\" content=\"0; url={target_filename}\">
  <script>window.location.replace('{target_filename}');</script>
</head>
<body>
  <main style=\"font-family: Arial, sans-serif; max-width: 720px; margin: 40px auto; line-height: 1.6;\">
    <h1>Publicação movida</h1>
    <p>Esta publicação foi reorganizada. Você será redirecionado automaticamente para a versão atual.</p>
    <p><a href=\"{target_filename}\">Acessar a publicação atual</a></p>
  </main>
</body>
</html>
"""
    old_path.write_text(html, encoding="utf-8")


def main():
    index_text = INDEX.read_text(encoding="utf-8")
    items = extract_news_items(index_text)
    existing = build_existing_index()
    mapping = []

    for item in items:
        old_url = item["url"]
        if not old_url.startswith("posts/"):
            continue
        if (ROOT / "noticias" / old_url).exists():
            continue
        score, target = choose_target(item, existing)
        if score < 0.60:
            raise RuntimeError(f"Correspondência insegura para {old_url}: score={score:.3f}, alvo={target['url']}")
        mapping.append((old_url, target["url"], score, target["title"]))

    for old_url, target_url, score, title in mapping:
        index_text = index_text.replace(f'"url": "{old_url}"', f'"url": "{target_url}"')
        create_redirect(old_url, target_url)

    INDEX.write_text(index_text, encoding="utf-8")

    report_lines = [
        "# Reparo de links 404 em notícias",
        "",
        f"Itens de notícias analisados: {len(items)}",
        f"Links quebrados corrigidos: {len(mapping)}",
        "",
        "| URL antiga | Novo alvo | Similaridade |",
        "|---|---|---|",
    ]
    for old_url, target_url, score, title in mapping:
        report_lines.append(f"| `{old_url}` | `{target_url}` | {score:.3f} |")
    (ROOT / "data" / "news_404_repair_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"Corrigidos {len(mapping)} links quebrados em noticias/index.html e criadas páginas de redirecionamento.")

if __name__ == "__main__":
    main()
