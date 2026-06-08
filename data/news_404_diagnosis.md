# Diagnóstico dos erros 404 em `/noticias/`

A página `noticias/index.html` não contém links estáticos no HTML principal; ela renderiza as publicações a partir da constante JavaScript `NEWS`. A auditoria local extraiu as URLs dessa constante e comparou cada caminho com os arquivos reais em `noticias/posts/`.

Resultado inicial: foram encontrados **97 itens** na matriz `NEWS`, dos quais **43 URLs apontavam para arquivos inexistentes**. A maioria dos erros está em publicações antigas, especialmente URLs geradas com identificador do Mercado Livre e timestamp, como `posts/analise-MLB4345564271-20260531.html` e `posts/analise-...-MLB...-20260602...html`.

A causa raiz é uma divergência entre os nomes antigos registrados na listagem de notícias e os nomes reais atualmente publicados em `noticias/posts/`. O conteúdo correspondente existe em grande parte dos casos, mas com slugs mais novos ou simplificados, por exemplo:

| URL antiga com 404 | Arquivo existente correspondente |
|---|---|
| `posts/analise-MLB4345564271-20260531.html` | `posts/analise-vale-a-pena-comprar-o-parafusadeira-furadeira-c-2-baterias-maleta-kit.html` |
| `posts/analise-MLB4292031849-20260531.html` | `posts/analise-vale-a-pena-comprar-o-cooktop-a-gas-fischer-4-bocas-fit-line-trempe.html` |
| `posts/analise-MLB4812143184-20260531.html` | `posts/analise-vale-a-pena-comprar-o-creatina-monohidratada-pura-500g-dark-lab-unidade.html` |
| `posts/top-20-produtos-mais-vendidos-20260604124146.html` | `posts/analise-top-20-produtos-mais-vendidos-as-melhores-ofertas-de-hoje-no-mercado.html` |

A correção recomendada é dupla: atualizar a matriz `NEWS` para apontar diretamente aos arquivos existentes e criar páginas de redirecionamento nos caminhos antigos, preservando acessos externos e URLs já indexadas.
