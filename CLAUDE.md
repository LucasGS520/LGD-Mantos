# Claude - Contexto e Instruções

## Sobre o Projeto *LGD Mantos*

O projeto é uma aplicação web-first de gestão interna para operação, análise
e marketing da loja LGD Mantos. O sistema centraliza dados de produtos, estoque,
compras, vendas e finanças, utilizando uma base única em PostgreSQL, backend
FastAPI e cliente web responsivo em React (PWA). A IA atua como camada auxiliar transversal,
apoiando decisões operacionais, análises e geração de conteúdo, sem substituir
o controle humano.

O principal papel do sistema é centralizar rotinas que normalmente ficariam
espalhadas em planilhas, anotações, WhatsApp ou controles manuais:

- Cadastro e controle de produtos.
- Gestão de estoque e movimentações.
- Controle de fornecedores.
- Registro de compras.
- Registro de vendas.
- Controle financeiro com DRE.
- Análises.
- Sugestões de reposição.

> Informações sobre a stack e tecnologias existentes em [STACK_LGD.md](STACK_LGD.md)

---

## Regras e Instruções de Execução

**Regras obrigatórias de economia (NÃO IGNORAR)**

1. NÃO liste árvore inteira do projeto (evite `tree`, `ls -R`, etc.). Se precisar, liste apenas pastas-alvo da fase.
2. NÃO leia arquivos completos sem necessidade. Prefira até 120 linhas por arquivo ou trechos específicos.
3. Priorize busca (`rg`/`grep`) para localizar pontos de mudança antes de abrir arquivos.
4. Não cole conteúdo integral de arquivos na resposta. Mostre apenas arquivos alterados, resumo do diff, comandos executados e resultados.
5. Execute somente uma fase por vez. Ao terminar a fase, pare e peça autorização para a próxima.
6. Se detectar duplicação ou mudança fora do escopo, interrompa e reporte.
