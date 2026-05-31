# Radar de Preços - Projeto Replicável

Este repositório contém o código-fonte de um site de curadoria de ofertas, otimizado para SEO e AdSense, com um robô de geração de conteúdo longo. Ele foi projetado para ser facilmente replicado em outras contas do GitHub para criar novos projetos de nicho.

## Visão Geral

O projeto inclui:

*   **Site Estático:** Construído com HTML/CSS simples, hospedado gratuitamente via GitHub Pages.
*   **Robô de Conteúdo:** Um script Python (`generate_blog_posts.py`) que gera artigos longos (mais de 1.000 palavras) e otimizados para SEO/EEAT a partir de uma lista de produtos.
*   **Links de Afiliados:** Integrado com o `matt_tool=vendas0nline` para rastreamento de comissões.
*   **Conteúdo Dinâmico:** O robô pode ser configurado para gerar posts sobre produtos específicos ou uma seleção aleatória dos melhores descontos.

## Como Replicar o Projeto

Siga os passos abaixo para configurar este projeto em sua nova conta do GitHub:

### 1. Crie um Novo Repositório no GitHub

1.  Faça login na sua conta do GitHub.
2.  Clique no botão `+` no canto superior direito e selecione `New repository`.
3.  Dê um nome ao seu repositório (ex: `meu-radar-de-ofertas`).
4.  **Marque-o como `Public`** (necessário para o GitHub Pages).
5.  Não inicialize o repositório com README, .gitignore ou licença.
6.  Clique em `Create repository`.

### 2. Clone o Repositório e Faça o Upload dos Arquivos

No seu terminal local, execute os seguintes comandos:

```bash
# Clone o repositório original (se ainda não o fez)
git clone https://github.com/radardeprecos/radar.git
cd radar

# Remova o histórico do git para iniciar um novo projeto
rm -rf .git

# Inicialize um novo repositório git
git init
git add .
git commit -m "Initial commit for new Radar project"

# Adicione o seu novo repositório remoto
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git

# Faça o push dos arquivos para o seu novo repositório
git branch -M main
git push -u origin main
```

**Importante:** Substitua `SEU_USUARIO` pelo seu nome de usuário do GitHub e `SEU_REPOSITORIO` pelo nome que você deu ao seu novo repositório.

### 3. Configure o GitHub Pages

1.  No seu novo repositório no GitHub, vá para `Settings`.
2.  No menu lateral esquerdo, clique em `Pages`.
3.  Em `Source`, selecione `Deploy from a branch`.
4.  Em `Branch`, selecione `main` e a pasta `/ (root)`.
5.  Clique em `Save`.

Seu site estará disponível em `https://SEU_USUARIO.github.io/SEU_REPOSITORIO/` em alguns minutos.

### 4. Personalize os Produtos (Opcional - Para Nicho)

Para ter produtos diferentes e focar em um nicho específico:

1.  Edite o arquivo `data/products/offers.json`.
2.  Você pode remover os produtos existentes e adicionar novos produtos manualmente, ou usar um script para buscar ofertas de um nicho específico (ex: apenas eletrônicos, apenas itens de beleza).
3.  **Certifique-se de que o `custom_affiliate_url` de cada produto contenha `matt_tool=vendas0nline` para garantir suas comissões.**

### 5. Execute o Robô de Geração de Conteúdo

Para gerar os artigos longos e atualizar o blog:

1.  Certifique-se de ter Python 3 instalado.
2.  No terminal, navegue até a pasta raiz do seu projeto (`cd SEU_REPOSITORIO`).
3.  Execute o robô:
    ```bash
    python3 scripts/generate_blog_posts.py
    ```
    Este comando irá gerar um novo artigo longo na pasta `noticias/posts/` com base nos produtos do `offers.json`.

### 6. Atualize o Blog com Todos os Posts (Opcional - Para Migrar Posts Antigos)

Se você tiver posts antigos (gerados pelo robô anterior) e quiser convertê-los para o formato longo, execute o script de migração:

```bash
python3 scripts/migrate_all_posts.py
```

### 7. Faça o Commit e Push das Alterações

Após gerar novos posts ou migrar os existentes, você precisa enviar as alterações para o GitHub:

```bash
git add .
git commit -m "Generated new blog posts / Migrated old posts"
git push origin main
```

Lembre-se de que o GitHub Pages pode levar alguns minutos para refletir as alterações.

---

**Dica:** Para automatizar a geração de posts, você pode configurar um GitHub Action para executar o `generate_blog_posts.py` periodicamente.
