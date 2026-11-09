# ADR 0001 — Monólito modular, autoridade e critérios de capacidade

Data: 2026-11-09. Estado: adotado para a execução A0–A9.

## Contexto e decisão

O produto tem um proprietário e correções retroativas que recalculam custos de outros acontecimentos. A confirmação já oferece uma transação única, replay puro e recibo idempotente. Distribuir essas responsabilidades acrescentaria coordenação sem demanda demonstrada.

Manter FastAPI/React/PostgreSQL, modelos ORM compartilhados e serialização global das mutações. Operações é a autoridade do ledger e das projeções de estoque/custo; Catálogo controla identidade/referências; Fotos controla seus metadados/arquivos; Auxiliares controla seus tipos. Histórico e Gestão são leitores. Escritas em auditoria, revisão global e recibos são transversais e coordenadas pelo caso de uso, sem commits intermediários em operações.

Entre módulos backend, consumir somente `public.py`. Gestão pode consumir replay/moeda pela interface pública de Operações; o ledger permanece puro. Imports de configuração/modelos compartilhados continuam permitidos fora do domínio. Frontend usa contratos públicos e o transporte recebe a sessão por configuração na composição, sem importar auth a partir de shared.

## Hipóteses e critérios

Enquanto não existir perfil informado pelo dono, medir 1 mil/10 mil/50 mil operações com 10/100/500 variantes, um dono e até quatro requisições simultâneas. Não são números de produção. As metas de investigação são 1 s para consultas simples, 2 s para prévia/confirmação e 5 s para gestão/correção; p95 com amostragem pequena é exploratório, sem SLA. A medição HTTP em processo não inclui rede, proxy ou navegador.

Primeiro reduzir carga de leitura, payloads e retenção de travas. Não introduzir checkpoint, cache ou projeção assíncrona nesta entrega sem evidência adicional e equivalência completa. Registrar o limite observado mesmo que a maior escala não atenda às metas; não transformar um limite excedido em alegação de capacidade.

## Fronteiras transacionais pretendidas

- Mutação/previsão operacional: trava exclusiva global, validação/replay, commit no encerramento da dependência, rollback integral em erro. A prévia continua sem reserva e sem criação de operação.
- Consultas compostas: transação somente de leitura com snapshot repetível; materializar dados antes de encerrar e calcular gestão sem manter trava de gravação.
- Fotos: arquivo imutável novo antes de metadados; commit explícito antes de remover arquivo anterior. Compensação em falha conhecida e reconciliação somente de leitura para interrupção incerta. Substituição mantém o ID da foto e troca arquivo/metadados em uma transação.
- Banco e disco não são transação única. Arquivo órfão é recuperável por relatório; referência sem arquivo é erro visível, nunca sucesso vazio.

## Alternativas e recuperação

Microserviços/filas, locks por variante, checkpoints e troca de roteador ficam descartados nesta execução por falta de necessidade demonstrada. Reconsiderar após perfil real ou metas excedidas no volume necessário. Manter navegação local: refresh perde contexto e rascunho, back do navegador não representa a pilha interna, e não há deep link. Essa limitação é registrada, sem persistir rascunho sensível.

Manter sessão JWT de 30 dias e localStorage neste produto de dono único: logout local não revoga token copiado. Rotacionar APP_SECRET invalida tokens e prévias de todos os dispositivos; exigir novo login e nova prévia. Não introduzir cookies/multiusuário. HTTPS é obrigatório em implantação pública; adicionar proteção limitada de tentativas de login e documentar seus limites por processo. Não afirmar que isso substitui auditoria de segurança.

## Verificação e dependências

Gates de dependências/ciclos, testes de snapshot, venda concorrente, repetição idempotente, falha de commit, arquivos e saúde. Medidas comparáveis ficam no resultado de Arquitetura. Schema e índices são decisões de Banco; backup externo, ensaio no servidor e RPO/RTO reais permanecem requisitos operacionais até evidência na implantação.
