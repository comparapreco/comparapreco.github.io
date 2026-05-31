#!/usr/bin/env python3
from pathlib import Path
path = Path('/home/ubuntu/recomendados/index.html')
html = path.read_text(encoding='utf-8')
old = 'onclick="Compara PreçoAuth.trackProductClick(${JSON.stringify(\'\').replace(\'""\',\'snapshot(product)\')})" href="${safe(url(product))}">Ver oferta</a></article>`; }).join(\'\'); }\n    async function fav(id){'
new = 'onclick="trackRec(\'${product.id}\')" href="${safe(url(product))}">Ver oferta</a></article>`; }).join(\'\'); }\n    function trackRec(id){ const p=products.find(x=>String(x.id)===String(id)); if(p) Compara PreçoAuth.trackProductClick(snapshot(p)); }\n    async function fav(id){'
if old not in html:
    raise SystemExit('Trecho antigo não encontrado')
path.write_text(html.replace(old, new), encoding='utf-8')
print('Rastreamento de recomendados corrigido.')
