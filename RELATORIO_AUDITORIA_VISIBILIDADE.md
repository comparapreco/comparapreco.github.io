# 🕵️ Relatório de Auditoria de Visibilidade — Radar de Preços

Após uma análise detalhada do site publicado (https://radardeprecos.github.io/radar/) e da estrutura de arquivos no repositório, identificamos as seguintes lacunas entre o que foi desenvolvido nas fases anteriores e o que está realmente acessível ao usuário final.

## 🔴 Problemas Críticos de Visibilidade

1.  **Menu de Exploração Oculto:** Existe um template completo (`templates/explorar_menu.html`) com links para Rankings, Comparativos, Estatísticas, Alertas e Ferramentas, mas ele **não está sendo incluído na Homepage (`index.html`)**. Isso torna quase impossível para um usuário comum descobrir essas funcionalidades.
2.  **Footer Incompleto:** O rodapé atual contém apenas links institucionais básicos (Sobre, Contato, etc.). Os links para Cupons, Black Friday e Rankings de 2026 não estão presentes no footer global.
3.  **Páginas Órfãs:** As páginas de `/estatisticas`, `/cupons`, `/black-friday` e `/melhores-2026` existem no servidor, mas não possuem links de entrada em nenhuma parte da navegação principal.

## 📊 Status das Funcionalidades (Fase 13 e anteriores)

| Funcionalidade | Status no Código | Visível no Site | Observação |
| :--- | :--- | :--- | :--- |
| **Rankings 2026** | ✅ Criado | ❌ Não | Acessível apenas via URL direta. |
| **Estatísticas** | ✅ Criado | ❌ Não | Link não existe no menu/footer. |
| **Cupons** | ✅ Criado | ❌ Não | Link não existe no menu/footer. |
| **Black Friday** | ✅ Criado | ❌ Não | Link não existe no menu/footer. |
| **Comparativos** | ✅ Criado | ❌ Não | Sistema de comparação existe mas não tem hub central. |
| **Alertas** | ✅ Criado | ❌ Não | Central de alertas não linkada. |

## 🚀 Plano de Correção Imediata (Antes da Fase 14)

1.  **Injeção do Menu de Exploração:** Atualizar o script `scripts/build_homepage.py` e o template `templates/homepage.html` para incluir a seção "Explorar o Radar".
2.  **Unificação do Header/Footer:** Criar um sistema de inclusão de componentes ou atualizar todos os arquivos `index.html` das subpastas para refletir a nova navegação.
3.  **Correção de Links Relativos:** Garantir que todos os links no menu de exploração funcionem tanto na home quanto nas subpáginas.

---

**Veredito:** O usuário tem razão. O site é tecnicamente robusto nos bastidores, mas a "vitrine" está escondendo 70% do valor gerado nas fases anteriores. A Fase 14 deve começar corrigindo essa exposição.
