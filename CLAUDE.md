# Claude - Contexto e Instruções

## Sobre o Projeto *LGD Mantos*

O projeto é uma aplicação de gestão interna para operação, análise
e marketing da loja LGD Mantos. O sistema centraliza dados de produtos, estoque,
compras, vendas e finanças, utilizando uma base única em PostgreSQL, backend
FastAPI e cliente web responsivo em React (PWA). A IA deve ser nativa dentro desse sistema, atuando como camada auxiliar transversal,
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

## Regras, Instruções de Execução e Uso de Tools (NÃO IGNORAR)

### Regras obrigatórias de economia

1. NÃO liste árvore inteira do projeto (`tree`, `ls -R`, etc.). Se precisar, liste apenas pastas-alvo da FASE atual.
2. Leia só o necessário pra decisão: comece com a tool `Grep` (não o comando `grep` cru) pra achar a linha certa, depois leia por trecho (`offset`/`limit`) a função/bloco relevante. Ler o arquivo inteiro se justifica quando for reescrever/entender a função por completo antes de editar (ex.: antes de `Edit`) ou quando o arquivo já for pequeno — nesses casos, fatiar a leitura por um limite arbitrário de linhas só custa turnos extras sem economizar nada.
3. Priorize a tool dedicada `Grep` — nunca o comando `grep`/`rg` cru via `Bash` — para localizar pontos de mudança antes de abrir arquivos, inclusive ao inspecionar diffs/arquivos de review. Reserve `Bash` pra comando de shell de verdade (git, docker, npm, alembic); usar `grep` via `Bash` só porque é mais rápido de digitar é a violação mais comum desta regra.
4. Não cole conteúdo integral de arquivos na resposta. Mostre apenas:
   - arquivos alterados (com caminho relativo)
   - resumo do diff — o que mudou e por quê
   - comandos executados e resultados relevantes
5. Execute somente **UMA FASE por vez**. Ao terminar, pare e peça autorização para a próxima.
6. Se detectar duplicação ou trabalho fora do escopo da FASE, interrompa e reporte antes de continuar.
7. Comentários e Docstrings devem ser explicativos, organizados e de fácil compreensão — pensados para manutenção e aprendizado contínuo.
8. Comentários e Docstrings devem **sempre** ser em português (PT-BR).
9. **Ao verificar via Docker/curl/psql em fluxos com múltiplos subagentes sobre o mesmo recurso**, registre credenciais e IDs de teste usados (arquivo de scratchpad ou ledger da execução) em vez de deixar cada subagente redescobrir o ambiente do zero — evita repetir login, criação e limpeza de dados de teste em cada dispatch.

### Regras de economia para fluxos com subagentes (implementador/revisor, Explore, Plan)

10. **O ritual completo de `superpowers:` (`brainstorming` → `writing-plans` → `subagent-driven-development` → revisão final de branch) é pra redesenho genuíno — não é o default pra qualquer tarefa.** Entre nele só quando pelo menos um destes for verdade: exige decisão de produto que só o usuário pode tomar (pergunte via `AskUserQuestion` antes de desenhar); mexe em 3+ arquivos com lógica nova relacionada; ou exige migration de schema. Bug fix, ajuste de validação, correção de UI, config/cache — usa `systematic-debugging` (quando for bug) + edição direta, sem passar por spec/plano. Uma vez dentro do ritual, as regras 11-15 abaixo continuam valendo por cima — o ritual completo não dispensa calibrar modelo/escopo, só decide QUANDO entrar nele.
11. **Não redespachar exploração de algo já lido na mesma sessão.** Antes de disparar um agente `Explore`/pesquisa, verifique se o arquivo/trecho já foi lido diretamente nesta conversa (mesmo antes de compactação — o resumo geralmente preserva o que foi aprendido). Só delegue exploração para território genuinamente não coberto ainda.
12. **Calibre o processo pelo risco/tamanho da task, não aplique o mesmo ritual pra tudo:**
    - Mudança mecânica de 1-2 arquivos com código já definido no plano (rename, mover função, adicionar parâmetro simples) → editar direto (`Edit`/`Write`), sem disparar par implementador+revisor. Reserve o ciclo completo de subagentes pra tasks com julgamento real, múltiplos arquivos, ou lógica de acesso/transação.
    - Ao planejar tasks (`writing-plans`/plan mode), agrupe passos mecânicos pequenos e correlatos numa única task em vez de fatiar em várias — cada task paga um custo fixo de despacho (brief, relatório, package, revisor) independente do tamanho.
    - Task puramente de verificação (rodar migration, conferir schema, checar boot — sem diff de código gerado) não precisa de par implementador+revisor: execute direto como controller.
    - **Antes de fechar a lista de tasks** de um plano que remove/renomeia um símbolo (enum, campo, endpoint, tipo), rode grep repo-wide (backend E frontend) por todas as ocorrências. Referência esquecida vira um ciclo implementador+revisor inteiro no meio da execução — bem mais caro que o grep antecipado.
13. **Verificação do implementador tem que ser evidência real, não raciocínio.** Ao despachar um subagente implementador, exigir explicitamente comando+saída real (curl, teste manual) para cada critério de verificação do brief — nunca aceitar "a lógica é simples, deve funcionar" como prova. Isso evita gastar um ciclo inteiro de revisão+fix só para completar verificação que devia ter sido feita na primeira passada.
14. **Escale o modelo do implementador E do revisor pelo tamanho/risco real da task**, não use sempre o mais caro por padrão. Se o brief já traz o código completo a escrever (transcrição), use o modelo mais barato disponível também para o implementador — só suba de nível quando a task exige julgamento real (múltiplos arquivos, lógica de acesso/transação nova não detalhada linha a linha no brief). Reserve o modelo mais capaz para a revisão final de branch (onde compensa, por pegar problemas de integração entre tasks) e para lógica de acesso/segurança.
15. **Para ajustes incrementais sobre um design já aprovado nesta sessão**, não repita brainstorming/exploração do zero — referencie o que já foi decidido e aprofunde só o que mudou. Rodar o ciclo completo (explorar→desenhar→planejar) só se justifica pra escopo genuinamente novo.

### Uso de Tools

#### graphify

Este projeto possui um grafo de conhecimento em graphify-out/ com nós principais, estrutura de comunidade e relações entre arquivos.

Regras:
- Para perguntas sobre a base de código, primeiro execute `graphify query "<pergunta>"` quando graphify-out/graph.json existir. Use `graphify path "<A>" "<B>"` para relações e `graphify explain "<conceito>"` para conceitos específicos. Esses comandos retornam um subgrafo delimitado, geralmente muito menor que GRAPH_REPORT.md ou a saída bruta do grep.
- Se graphify-out/wiki/index.md existir, use-o para navegação ampla em vez de navegar diretamente pelo código-fonte.
- Leia graphify-out/GRAPH_REPORT.md apenas para revisão da arquitetura geral ou quando query/path/explain não fornecerem contexto suficiente.
- Após modificar o código, SEMPRE EXECUTE `graphify update .` para manter o grafo **atualizado e alinhado com as modificações executadas** (somente AST, sem custo de API).
- `graphify update` gera arquivos de cache em `graphify-out/cache/` — SEMPRE exclua `graphify-out/cache` (e `graphify-out/<data>/` de backup) de pacotes de diff/revisão gerados pra subagentes revisores; eles não são código revisável e só inflam o pacote.

#### caveman

Plugin de compressão de saída e subagentes leves (`cavecrew-*`), usado aqui como ferramenta de economia de créditos — não confundir com as regras de economia de leitura/subagentes acima, que continuam valendo por cima disso.

Regras:
- O modo de conversa (`/caveman`, ativo por padrão nesta sessão) comprime só o TEXTO que vai pro usuário — nunca aplique a lógica de compressão a código, comentários, docstrings, mensagens de commit ou PRs (já é a fronteira nativa do plugin; reforçando aqui porque a Regra 8 exige comentário/docstring explicativo em PT-BR, que precisa continuar completo, não comprimido).
- Para tarefa de **localizar código** ("onde é definido X", "quem chama Y", mapear pasta) sem precisar de julgamento/sugestão de fix, prefira o subagente `caveman:cavecrew-investigator` a um `Explore` genérico — mesmo resultado, ~60% menos tokens no relatório.
- Para **edição cirúrgica de 1-2 arquivos** com escopo já óbvio (typo, rename mecânico, reescrita de uma função só) — o mesmo tipo de task da Regra 12 que dispensa par implementador+revisor — considere `caveman:cavecrew-builder` em vez de editar você mesmo quando quiser um "recibo" de diff formal sem gastar o ciclo completo de subagent-driven-development. Ele recusa escopo de 3+ arquivos por design — não force além disso.
- Para revisão de diff/PR de **baixo risco** (mudança pequena, mecânica, sem lógica de acesso/transação envolvida), `caveman:cavecrew-reviewer` (uma linha por achado, sem elogio, sem escopo extra) é mais barato que o template completo de revisor do subagent-driven-development — reserve o template completo pra tasks de risco real (mesmo critério da Regra 14).
- `caveman-compress <arquivo.md>` reduz ~46% dos tokens de entrada de documentos longos — útil pra comprimir specs/planos antigos antes de referenciá-los como contexto histórico (não use em specs/planos ativos que ainda serão lidos por humano ou citados literalmente por subagente, só em material de arquivo).
- `caveman-commit`/`caveman-review` (mensagens de commit e comentários de PR curtos) ficam disponíveis mas são de uso opcional do usuário — não acione automaticamente, já que Regra do projeto é usuário controla git.
