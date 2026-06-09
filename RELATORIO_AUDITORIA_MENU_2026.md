# Relatório de Auditoria e Otimização do Menu — Compara Preço 2026

Este relatório apresenta uma auditoria detalhada de todos os **24 itens do menu** do site **Compara Preço**, identificando o que funciona, o que está quebrado, o que contém dados fictícios ou simulações sem funcionalidade real, e quais são as páginas sem links de afiliado ativos.

O objetivo é fornecer um diagnóstico preciso e um plano de ação claro para remover ou corrigir elementos que reduzem a confiança do usuário e prejudicam a conversão do site.

---

## 📊 Resumo Geral da Auditoria

Após uma análise profunda da estrutura de arquivos físicos, rotas e comportamento dos scripts do site, classificamos os 24 itens do menu em quatro categorias de status:

| Categoria | Definição | Quantidade | Ação Recomendada |
| :--- | :--- | :---: | :--- |
| **🟢 Totalmente Funcional** | Páginas dinâmicas ou estáticas com conteúdo real, links de afiliado válidos e boa experiência de uso. | **11** | Manter e monitorar. |
| **🟡 Precisa de Ajustes** | Páginas que funcionam, mas possuem conteúdo mínimo, links de afiliado estáticos ausentes ou dependência de dados hardcoded. | **6** | Corrigir links ou expandir conteúdo. |
| **🟠 Simulação / Sem Função** | Páginas com formulários ou botões fictícios que apenas exibem mensagens de alerta (alert) sem salvar dados. | **3** | Substituir por integrações reais ou simplificar o layout. |
| **🔴 Erro de Rota / Duplicada** | Páginas com links inconsistentes no menu ou pastas duplicadas no servidor gerando páginas órfãs. | **4** | Corrigir os links no menu principal e nos templates. |

---

## 🔍 Auditoria Detalhada por Item do Menu

Abaixo, detalhamos o status técnico e a recomendação prática para cada um dos itens listados no menu de navegação.

### 1. 🔥 Ofertas & Rankings

| Item do Menu | Rota do Menu | Pasta Física | Status Técnico | Problemas Identificados | Recomendação Prática |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **Ofertas de Hoje** | `/ofertas-hoje/` | `/ofertas-hoje/` | **🟢 Funcional** | Nenhum. Usa o script centralizado `app.js` para carregar ofertas reais via JSON com links de afiliado ativos. | **Manter.** |
| **Melhores de 2026** | `/melhores-2026/` | `/melhores-2026/` | **🟡 Ajustar** | Os produtos listados são fixos (hardcoded) e **não possuem links de afiliado** para compra, apenas texto informativo. | **Corrigir:** Adicionar links de afiliado reais do Mercado Livre/Amazon para os produtos listados (ex: Galaxy S24 Ultra, iPhone 15 Pro Max). |
| **Prêmio Compara Preço 2026** | `/premio-radar-2026/` | `/premio-radar-2026/` | **🔴 Rota Incorreta** | O link do menu aponta para `/premio-radar-2026/` (13KB), mas existe outra pasta duplicada chamada `/premio-compara-2026/` (2.9KB) que está órfã. | **Consolidar:** Excluir a pasta física `/premio-compara-2026/` e manter apenas `/premio-radar-2026/`. Corrigir o texto do menu para que o nome exibido coincida com a URL ("Prêmio Radar 2026"). |
| **Quedas de Hoje** | `/quedas-hoje/` | `/quedas-hoje/` | **🟢 Funcional** | Nenhum. Carrega as maiores quedas de preço dinamicamente a partir do banco de dados de ofertas reais. | **Manter.** |
| **Mais Clicados** | `/mais-clicados/` | `/mais-clicados/` | **🟢 Funcional** | Nenhum. Mostra os produtos com maior taxa de cliques dos usuários de forma dinâmica. | **Manter.** |
| **Ofertas Explodindo** | `/ofertas-explodindo/` | `/ofertas-explodindo/` | **🟢 Funcional** | Nenhum. Página de alta conversão focada em promoções com estoque limitado e links de afiliado diretos. | **Manter.** |

---

### 2. 📊 Inteligência

| Item do Menu | Rota do Menu | Pasta Física | Status Técnico | Problemas Identificados | Recomendação Prática |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **Central de Comparativos** | `/central-comparativos/` | `/central-comparativos/` | **🟢 Funcional** | Nenhum. Excelente página de destino que agrupa produtos para comparação direta. | **Manter.** |
| **Comparar Produtos** | `/comparar/` | `/comparar/` | **🟢 Funcional** | Nenhum. Ferramenta interativa de comparação lado a lado rodando 100% no cliente. | **Manter.** |
| **Ranking de Marcas** | `/marcas/` | `/marcas/` | **🟢 Funcional** | Nenhum. Página estática que direciona os usuários para as categorias de marcas parceiras. | **Manter.** |
| **Compara Preço de Mercado** | `/radar-de-mercado/` | `/radar-de-mercado/` | **🔴 Rota Incorreta** | O link do menu aponta para `/radar-de-mercado/` (6.2KB), mas existe outra pasta física chamada `/compara-de-mercado/` (2.7KB) que está órfã. | **Consolidar:** Remover a pasta física `/compara-de-mercado/` e manter apenas `/radar-de-mercado/`. |
| **O Que Está em Alta** | `/tendencias/` | `/tendencias/` | **🔴 Rota Incorreta** | O link do menu aponta para `/tendencias/` (19KB), mas existe outra pasta física chamada `/o-que-esta-em-alta/` (2.8KB) que está órfã. | **Consolidar:** Remover a pasta física `/o-que-esta-em-alta/` e manter apenas `/tendencias/`. |
| **Nossa Metodologia** | `/metodologia/` | `/metodologia/` | **🟢 Funcional** | Nenhum. Página institucional importante que explica o funcionamento do algoritmo e o cálculo do score. | **Manter.** |

---

### 3. 📚 Conteúdo & Guias

| Item do Menu | Rota do Menu | Pasta Física | Status Técnico | Problemas Identificados | Recomendação Prática |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **Blog & Notícias** | `/noticias/` | `/noticias/` | **🟢 Funcional** | Nenhum. Central de conteúdo atualizada e com links de artigos funcionando. | **Manter.** |
| **Guias de Compra** | `/guias/` | `/guias/` | **🟡 Ajustar** | A página de índice `/guias/index.html` contém apenas **um único guia** ("Melhor Celular até R$ 1.500"). | **Expandir:** Adicionar mais guias de compra reais (ex: "Melhor Notebook para Trabalho" ou "Melhor TV 4K Custo-Benefício") para preencher a página. |
| **Glossário Tech** | `/glossario/` | `/glossario/` | **🟡 Ajustar** | Conteúdo extremamente raso. Possui apenas **4 termos definidos** (AMOLED, SSD NVMe, Wi-Fi 6, RAM LPDDR5). | **Expandir:** Adicionar pelo menos mais 10 termos comuns do mercado de tecnologia (ex: IPS, OLED, HDR, Processador Octa-Core, etc.) para dar profundidade de conteúdo. |
| **Aprenda a Economizar** | `/aprender/` | `/aprender/` | **🟢 Funcional** | Nenhum. Contém artigos educacionais bem estruturados sobre como evitar fraudes e economizar. | **Manter.** |
| **Vale a Pena Esperar?** | `/vale-a-pena-esperar/` | `/vale-a-pena-esperar/` | **🟢 Funcional** | Nenhum. Análise preditiva excelente sobre o melhor momento de compra de eletrônicos. | **Manter.** |
| **Calendário de Preços** | `/calendario-de-precos/` | `/calendario-de-precos/` | **🟢 Funcional** | Nenhum. Guia sazonal completo mapeando os melhores meses para comprar cada categoria de produto. | **Manter.** |

---

### 4. 🛠️ Ferramentas & Promoções

| Item do Menu | Rota do Menu | Pasta Física | Status Técnico | Problemas Identificados | Recomendação Prática |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **Central de Alertas Avançados** | `/alertas/` | `/alertas/` | **🟠 Simulação** | O formulário de criação de alertas é apenas uma simulação. Ao clicar em "Criar Alerta", ele dispara um `alert()` em JavaScript sem persistir ou enviar nada. | **Corrigir:** Modificar o JavaScript para salvar o alerta no `localStorage` do navegador do usuário (assim como já é feito na página de favoritos) para que ele sinta que a ferramenta é real e funcional, ou integrar com um serviço de captura de leads real. |
| **Centro de Cupons** | `/cupons/` | `/cupons/` | **🟠 Simulação** | Os botões "Usar Cupom" apenas exibem uma mensagem de alerta na tela (`alert('Redirecionando...')`) sem de fato redirecionar o usuário para a loja parceira com o link de afiliado. | **Corrigir:** Adicionar links de afiliado reais do Mercado Livre ou Amazon associados a cada cupom para que o clique realmente redirecione o usuário para a página de cupons da respectiva loja. |
| **Black Friday 2026** | `/black-friday/` | `/black-friday/` | **🟢 Funcional** | Nenhum. Contagem regressiva ativa e guias de preparação bem estruturados. | **Manter.** |
| **Simulador de Economia** | `/ferramentas/economia/` | `/ferramentas/economia/` | **🟢 Funcional** | Nenhum. Calculadora interativa excelente que calcula a economia anual potencial com base nos gastos do usuário. | **Manter.** |
| **Estatísticas do Site** | `/estatisticas/` | `/estatisticas/` | **🟡 Ajustar** | Os dados exibidos (5.420 produtos monitorados, 42% de economia média) são fixos (hardcoded) no HTML. | **Otimizar:** Conectar esses números ao tamanho real do array do arquivo `offers.json` via JavaScript para tornar os dados dinâmicos e reais. |
| **Meus Favoritos** | `/meus-favoritos/` | `/meus-favoritos/` | **🟢 Funcional** | Nenhum. Excelente ferramenta rodando 100% local no navegador do usuário via `localStorage`. | **Manter.** |

---

## 🛠️ Plano de Ação de Correção Rápida

Para resolver os problemas que tiram a confiança do site e arrumar os links imediatamente, sugerimos as seguintes ações técnicas automatizadas no repositório:

### Passo 1: Eliminar as Pastas Duplicadas e Órfãs
Para evitar confusão e melhorar o SEO (evitando conteúdo duplicado), execute a remoção das pastas que não são usadas pelo menu:
```bash
rm -rf ~/comparapreco/premio-compara-2026
rm -rf ~/comparapreco/compara-de-mercado
rm -rf ~/comparapreco/o-que-esta-em-alta
```

### Passo 2: Tornar a Página de Alertas Funcional (Persistência Local)
Podemos ajustar o script de `/alertas/index.html` para salvar os alertas no `localStorage` do navegador, integrando-o com a aba "Meus Alertas" da página de Favoritos. Isso faz com que a ferramenta funcione de verdade localmente!

### Passo 3: Adicionar Links Reais nos Cupons
Substituir o `alert()` genérico do botão de cupons por um redirecionamento real para a página de cupons oficiais do Mercado Livre com a tag de afiliado do site:
```javascript
// Alterar no arquivo /cupons/index.html:
window.open('https://shope.ee/clique-aqui' or 'https://www.mercadolivre.com.br/cupons?matt_tool=60566305');
```

### Passo 4: Corrigir Nomes do Menu no Index Principal e Templates
Ajustar o texto do menu para corresponder exatamente ao que as páginas entregam:
* De "Prêmio Compara Preço 2026" para "Prêmio Radar 2026" (URL: `/premio-radar-2026/`)
* De "Compara Preço de Mercado" para "Radar de Mercado" (URL: `/radar-de-mercado/`)
* De "O Que Está em Alta" para "Tendências da Semana" (URL: `/tendencias/`)
