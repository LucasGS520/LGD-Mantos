# Produto e objetivo do LGD Mantos

> **Status:** definição de produto consolidada em 2026-10-27
>
> **Finalidade:** servir como fonte oficial das decisões de produto que orientarão requisitos, critérios de aceite e planejamento técnico

---

## Propósito do Sistema

### Definição do produto

O LGD Mantos é a central interna de operações, controle e gestão da loja LGD Mantos. Ele deve reunir informações e rotinas essenciais do negócio em uma fonte única, confiável e rastreável, permitindo ao dono acompanhar a operação, compreender a situação da loja e tomar decisões.

Além de servir ao uso direto do dono, o sistema deve funcionar como base de dados da loja para outras camadas, ferramentas e fluxos de trabalho. Essas soluções externas poderão consumir os dados registrados no LGD Mantos, mas não passam automaticamente a fazer parte de sua responsabilidade.

### Problema que o produto resolve

Atualmente, a loja não possui um controle central para sua operação e gestão. Sem o produto, informações e rotinas podem ficar dispersas em planilhas, anotações, conversas ou controles manuais, dificultando a obtenção de uma visão confiável do negócio.

O LGD Mantos existe para substituir essa ausência de controle por uma base operacional e gerencial capaz de responder, entre outras, perguntas como:

- O que a loja possui em estoque?
- O que entrou, saiu ou foi ajustado?
- O que foi vendido, por qual canal e com qual resultado?
- Qual foi o resultado das compras e vendas registradas?
- O que precisa ser reposto?
- Quais produtos merecem atenção comercial?

A inexistência atual de um controle central foi declarada pelo dono e é tratada como **fato atual do negócio**. A centralização dessas informações e rotinas no LGD Mantos é uma **decisão de produto**.
Um **sistema de usuário unico** - O produto deve oferecer controle e visão ampla sobre as diferentes áreas da loja, com camadas simples, coerentes e interligadas, evitando navegação confusa ou fragmentação do entendimento.

### Valor esperado

O valor do produto está organizado em três frentes complementares:

1. **Controle operacional:** registrar corretamente os acontecimentos da loja e manter seu histórico.
2. **Controle gerencial:** transformar os registros em uma visão clara do negócio e em apoio à decisão.
3. **Habilitação de valor externo:** disponibilizar dados corretos e úteis para ferramentas e fluxos especializados que ajudem a loja a vender e gerar resultados.

As três frentes pertencem à visão do produto, mas não possuem a mesma prioridade. O controle operacional confiável forma o núcleo obrigatório; a informação gerencial evolui sobre registros reais e consistentes; e a habilitação de valor externo permanece como qualidade estrutural dos dados até que exista um consumidor concreto.

### Limite central de responsabilidade

O LGD Mantos não pretende concentrar toda atividade necessária à loja. Sua responsabilidade é:

- centralizar o controle interno e a gestão;
- preservar dados corretos, coerentes, rastreáveis e reutilizáveis;
- permitir a consulta interna dos dados e preservá-los em condições de futura reutilização externa;
- fornecer contexto confiável para ferramentas externas executarem atividades especializadas.

O sistema não precisa executar a etapa especializada apenas porque fornece os dados usados nela. Por exemplo: deve manter informações confiáveis sobre produtos e disponibilizá-las para um fluxo de marketing, mas a criação da arte de uma publicação pode ocorrer em outra ferramenta.

Nenhum mecanismo externo de disponibilização faz parte do núcleo atual. Relatórios exportáveis, arquivos, APIs ou integrações somente poderão ser escolhidos diante de uma necessidade e de um consumidor reais.

---

## Operação real da loja

O ponto de partida real da loja, e não um processo ideal nem uma validação automática das práticas atuais como regras permanentes. Os fatos abaixo servem como evidência para a discussão; não definem, por si mesmos, como o produto deverá funcionar.

### Diagnóstico geral

A operação não possui hoje registros consolidados de estoque, compras, vendas, recebimentos, fornecedores ou canais. O dono não consegue consultar com segurança a situação atual da loja e reconhece dificuldade em manter controles e rotinas de gestão manualmente.

Esse cenário é um **fato atual do negócio**. Foi decidido que o controle começará pela formação de um inventário inicial e seguirá dali em diante, sem reconstruir o passado com estimativas, suposições ou dados sem confiança.

O inventário inicial representará o ponto zero da operação controlada. Serão registrados os dados conhecidos quando o sistema estiver pronto para uso; informações desconhecidas não serão inventadas nem impedirão o início do controle.

### Compras e entrada de peças

O fluxo atual de compra ocorre assim:

1. O dono percebe que existe dinheiro disponível para comprar ou que está se aproximando um período em que considera importante reforçar o estoque.
2. A compra é realizada presencialmente nos fornecedores.
3. Não existe planejamento prévio do que comprar, orçamento formal, lista de necessidades ou meta de composição do estoque.
4. Antes da visita, não há certeza sobre quais marcas, modelos, tamanhos, cores ou estampas estarão disponíveis.
5. A escolha acontece no momento da compra, baseada principalmente na percepção do que vendeu melhor, recebeu mais aceitação ou parece ter potencial.
6. As peças adquiridas passam a compor um estoque físico que atualmente não está registrado de forma confiável.

Existem fornecedores preferidos, mas ainda não há cadastro ou histórico que permita comparar fornecedores, características das peças, compras e resultados de venda.

#### Problemas observados nas compras

- não há visibilidade confiável do estoque existente antes de comprar;
- não há histórico estruturado que indique o que vendeu, encalhou ou foi mais aceito;
- não há critérios objetivos de reposição ou composição do estoque;
- não há planejamento por marca, modelo, tamanho, cor, estampa ou público;
- não há controle consolidado de fornecedores e canais de compra;
- disponibilidade financeira e necessidade de estoque são percebidas informalmente.

#### Registro da compra

A compra será registrada como um acontecimento único e direto. O produto não criará etapas de intenção, planejamento, aprovação, pedido ou compra em andamento.

O registro terá somente:

- data da compra, preenchida automaticamente e editável;
- fornecedor;
- canal de compra;
- itens adquiridos;
- quantidade de cada item;
- custo unitário de cada item;
- valor total, calculado automaticamente;
- observação opcional.

Ao salvar a compra, os itens entram no estoque e o custo fica registrado. A compra poderá ser editada posteriormente; quantidades, estoque e totais deverão ser recalculados automaticamente. Um registro lançado por engano poderá ser anulado, desde que o sistema reverta seus efeitos sem produzir estoque negativo ou inconsistência com vendas posteriores e preserve o histórico da operação.

O apoio a compras futuras será produzido a partir do histórico de compras, estoque e vendas. Ele não será representado por estados adicionais dentro do registro da compra.

#### Natureza do produto e da recompra

Uma mesma estampa quase nunca é comprada novamente. A recorrência acontece principalmente em características como marca e modelo, enquanto a peça ou estampa específica tende a não ser reposta.

Portanto, o produto não deve pressupor que “reposição” significa recomprar o mesmo item ou SKU. O apoio à compra deverá analisar características que funcionaram bem — como marca, categoria, modelo e tamanho — mesmo quando a próxima estampa for diferente.

### Controle e estados do estoque

Foi decidido que o sistema deverá permitir ao dono conhecer o estoque sem precisar conferir fisicamente todas as peças a cada consulta. O controle precisa informar, pelo menos, quais itens existem e seus modelos e tamanhos.

Peças idênticas serão controladas por quantidade, sem identificação individual. Quando características comercialmente relevantes forem diferentes, os itens deverão ser distinguíveis; quando forem iguais, uma quantidade agregada será suficiente.

Também foi decidido preservar a simplicidade operacional para um único usuário. O controle essencial será saber a quantidade disponível e reconhecer quando o item está fora do estoque. O sistema não controlará empréstimo, deslocamento ou demonstração de peças; essas situações estão **fora do escopo**.

### Venda e entrega

O volume atual de vendas é baixo. Pelo histórico percebido pelo dono, o contato presencial, levando os produtos até potenciais clientes, é a forma que mais favoreceu a conversão.

O fluxo mais comum relatado é:

1. O contato e a negociação podem acontecer de maneira informal e presencial.
2. O cliente avalia os produtos e decide quais deseja comprar.
3. Quando confirma a compra, fica com a peça.
4. O pagamento costuma ocorrer por Pix.
5. Em alguns casos, o cliente paga uma parte no momento e o restante posteriormente.
6. A própria loja pode assumir o deslocamento e a entrega dos itens.

O pagamento parcial cria um saldo a receber no registro da venda. O sistema controlará o valor financeiro pendente, mas não controlará quem é o cliente ou de quem o valor deverá ser cobrado.

Foi decidido que o LGD Mantos controlará as vendas e a saída dos produtos do estoque causada por elas. O controle deverá preservar a flexibilidade comercial atual, incluindo pagamentos divididos e descontos negociados conforme o contexto ou a quantidade.

Foi definido que a venda é considerada realizada quando o cliente confirma a compra. Nesse momento, a quantidade vendida deve sair do estoque, independentemente de o pagamento estar completo. Estoque e recebimento financeiro serão controles separados.

Flexibilidade não significa ausência de registro: a intenção validada é registrar o que foi combinado e o que efetivamente aconteceu para que o dono possa controlar a operação e tomar decisões posteriormente.

#### Valores e preço efetivo da venda

Foi decidido que o sistema manterá valores cadastrados para auxiliar o dono no momento da venda. O preço cadastrado será uma referência operacional, não uma obrigação: o preço efetivamente praticado poderá ser ajustado em cada venda.

Cada item terá custo e preço de venda de referência cadastrados. O registro deverá preservar a referência disponível no momento e o preço efetivamente negociado. Isso permitirá conhecer descontos e variações sem impedir a flexibilidade comercial.

O desconto não terá um campo próprio: será calculado pela diferença entre o preço de referência e o preço praticado. O usuário informará diretamente o preço negociado.

#### Campos mínimos da venda

Para registrar uma venda, o usuário informará somente:

- canal de venda;
- itens e respectivas quantidades;
- preço efetivamente praticado em cada item;
- pagamento inicial, quando houver, com valor e forma de pagamento;
- observação opcional.

O sistema preencherá a data automaticamente e obterá do cadastro o custo e o preço de referência. Também calculará valor total, desconto implícito, saldo e situação financeira.

A venda não terá fornecedor, cliente, etapas, aprovação ou estado “em andamento”. Confirmar a venda será uma ação única: registra a operação e retira imediatamente as quantidades vendidas do estoque.

A venda poderá ser editada posteriormente. Alterações em itens, quantidades, preços ou pagamentos deverão recalcular estoque, totais, saldo e situação. Um registro criado por engano poderá ser anulado com confirmação, restaurando as quantidades, retirando seus efeitos financeiros e preservando o histórico da operação.

O produto não terá cadastro, identificação ou controle de clientes. A observação poderá registrar livremente algum contexto necessário para o dono, inclusive sobre acordos ou pagamentos parciais, sem transformar essas informações em um modelo de cliente.

Essa escolha possui uma limitação aceita: o sistema conseguirá informar o total a receber e a situação financeira de cada venda, mas não conseguirá agrupar dívidas, histórico ou comportamento por cliente.

#### Controle dos pagamentos

O sistema não exigirá um plano rígido de parcelas. Ele registrará a realidade financeira da venda:

- a venda preserva o preço de referência dos itens, os preços praticados e o valor final;
- cada pagamento recebido é registrado separadamente com valor e forma de pagamento;
- o momento do registro pode ser armazenado automaticamente, sem exigir controle manual de datas;
- o saldo a receber é calculado pela diferença entre o valor final e a soma dos pagamentos;
- qualquer venda com saldo maior que zero é tratada simplesmente como **pendente**, mesmo que parte do valor já tenha sido recebida;
- quando o saldo chega a zero, a venda é tratada como **concluída**;
- observações podem registrar acordos excepcionais sem criar um novo fluxo para cada caso.

A venda poderá ser confirmada mesmo sem pagamento inicial e permanecer pendente enquanto houver saldo. Novos pagamentos poderão ser acrescentados posteriormente até sua conclusão financeira.

Pagamentos poderão ser editados ou removidos. Depois de qualquer inclusão, edição ou remoção, saldo e situação serão recalculados automaticamente. Uma venda anteriormente concluída voltará a ser pendente se uma correção fizer surgir saldo novamente.

Valores e formas de pagamento deverão permanecer em campos estruturados; a observação servirá apenas para contexto complementar. Não haverá vencimento, agenda de parcelas, cobrança ou acompanhamento de datas combinadas.

### Canais de compra e venda

Foi decidido controlar, de maneira simples, os canais pelos quais compras e vendas são realizadas. Canal servirá como uma classificação do contexto da operação e não deverá criar fluxos diferentes ou aumentar a complexidade do registro.

#### Compra

O canal efetivamente utilizado hoje é a compra presencial diretamente com fornecedores. Entrega por fornecedor e compras por outros canais são possibilidades conhecidas, mas ainda não constituem um fluxo recorrente nem controlado.

#### Venda

O canal efetivo é a venda direta e presencial, com possibilidade de deslocamento dos itens até o cliente. A presença em rede social existe, mas possui alcance e giro baixos e ainda não funciona como um canal relevante de vendas.

A LGD Mantos **não pretende abrir uma loja física**. O produto não precisa controlar como as peças foram apresentadas ou transportadas antes da venda.

Para evitar conceitos misturados, ficou definido que:

- **canal de compra** identifique por onde a compra foi realizada, como presencial ou outro canal futuro;
- **canal de venda** identifique por onde a venda se originou ou foi fechada;
- **forma de pagamento** seja registrada separadamente e não seja tratada como canal;
- entrega e deslocamento permaneçam fora desse controle, salvo nova necessidade real.

### Pós-venda e exceções

Foi decidido que o produto não cobrirá processos de pós-venda neste momento. Troca, devolução, defeito e outros tratamentos posteriores à venda ficam **fora do escopo desta fase**.

Essa exclusão evita criar regras para casos que ainda não ocorreram e não demonstraram valor suficiente. Caso uma necessidade real apareça, o tema deverá voltar à descoberta antes de qualquer implementação.

### Consulta e controle

Não existem hoje consultas diárias, semanais ou mensais estabelecidas. O dono frequentemente não sabe qual é a situação da loja porque os acontecimentos não são registrados de maneira consolidada.

O controle gerencial mínimo desta operação deverá responder, sob consulta e sem impor uma rotina fixa:

- quais itens e quantidades estão disponíveis;
- quais compras foram registradas e quanto custaram;
- quais vendas foram registradas e quais itens saíram;
- quanto foi vendido, recebido e permanece pendente;
- quais canais foram utilizados nas compras e vendas;
- quais marcas, modelos, estampas, cores e tamanhos aparecem nas compras, no estoque e nas vendas.

As análises gerenciais e recomendações definidas nas rodadas posteriores complementam esse controle sem reabrir as regras operacionais consolidadas nesta seção.

Os indicadores e a frequência de acompanhamento deverão nascer das decisões que o dono precisa tomar, e não apenas dos dados ou dashboards que o sistema já possui.

---

## Regras de negócio

Esta seção define as condições, validações, cálculos e regras de rastreabilidade que sustentam a consistência da operação. Ela não cria novos fluxos para situações hipotéticas nem amplia o escopo operacional já definido.

### Identidade do item

O catálogo separará **produto** de **variante**:

- o produto representa uma peça comercial identificada principalmente por sua estampa;
- tamanho e cor formam as variantes do produto;
- cada combinação de produto, tamanho e cor possui sua própria quantidade em estoque;
- unidades com a mesma combinação são agregadas, sem identificação individual;
- marca, modelo e categoria descrevem o produto, mas não criam sozinhos um novo item;
- material não será cadastrado ou utilizado na identidade do item;
- cada variante receberá um código interno gerado automaticamente, sem exigir a criação manual de SKU.

Os campos essenciais serão:

- nome ou descrição curta;
- estampa;
- marca;
- modelo;
- categoria;
- tamanho;
- cor;
- custo de referência;
- preço de venda de referência;
- observação opcional.

Para evitar duplicidades, o sistema comparará valores após normalizar diferenças de espaços, maiúsculas, minúsculas e acentuação. Uma combinação exatamente repetida de produto, tamanho e cor será impedida. Nomes apenas semelhantes produzirão um alerta, mas a decisão de manter registros distintos continuará com o dono. O sistema não unirá cadastros automaticamente.

### Inventário inicial

O inventário inicial será realizado uma única vez, quando começar o uso real do sistema, e formará o ponto zero da operação controlada. Cada variante receberá sua quantidade inicial.

Informações desconhecidas não serão inventadas. No inventário inicial, custo ou preço de referência desconhecido poderá permanecer sem valor. Depois do início da operação, diferenças entre o sistema e o estoque físico serão tratadas por ajustes de estoque, sem reabrir o inventário como rotina.

Uma correção excepcional do inventário inicial continuará possível. Ela deverá preservar o valor anterior, o novo valor, o momento e o motivo da alteração.

### Estoque e ajustes

Existe um único estoque geral da loja. Não haverá locais, transferências ou saldos separados.

O estoque será alterado por inventário inicial, compra, venda ou ajuste manual. Compra e venda criarão suas movimentações automaticamente e essas movimentações não poderão ser editadas diretamente: qualquer correção deverá ocorrer no registro de origem.

O ajuste manual terá somente duas direções:

- **entrada**, que aumenta a quantidade disponível;
- **saída**, que reduz a quantidade disponível.

Cada ajuste registrará variante, quantidade, direção, motivo curto obrigatório, observação opcional e data e hora automáticas. Perda, avaria, uso próprio e divergência de contagem serão tratados por esse mesmo mecanismo, sem fluxos ou estados próprios. Nenhuma saída ou correção poderá produzir estoque negativo.

### Validações de compras e vendas

- quantidades devem ser números inteiros maiores que zero;
- valores monetários não podem ser negativos;
- uma compra exige custo unitário maior que zero; custo desconhecido somente será aceito no inventário inicial;
- uma venda exige preço praticado maior que zero;
- o preço praticado pode ser menor ou maior que o preço de referência;
- uma venda somente pode ser confirmada quando todas as quantidades solicitadas estiverem disponíveis;
- a disponibilidade será verificada novamente no momento da confirmação;
- se qualquer item estiver indisponível, toda a operação será recusada, sem baixa parcial silenciosa;
- alterações serão aplicadas como uma única operação e recalcularão todos os seus efeitos;
- se uma alteração produzir estoque negativo, pagamento excedente ou outra inconsistência, ela será recusada integralmente e o registro permanecerá inalterado.

Uma retirada gratuita não será registrada como venda com valor zero. Ela será um ajuste de saída, acompanhado de seu motivo.

### Correções e anulações

Compras e vendas poderão ser corrigidas enquanto seus efeitos puderem ser recalculados sem quebrar a consistência da operação. A edição aplicará ao estoque e aos valores somente a diferença entre a versão anterior e a nova.

Acontecimentos operacionais não serão apagados definitivamente. Um registro criado por engano será **anulado**:

- a anulação preservará o registro original e seu histórico;
- a anulação de uma compra reverterá sua entrada somente se o resultado não deixar o estoque negativo;
- a anulação de uma venda devolverá as quantidades ao estoque e desconsiderará seus efeitos financeiros;
- toda edição ou anulação exigirá confirmação e um motivo curto;
- se a correção não puder ser aplicada com segurança, nenhuma parte dela será salva.

Essa regra oferece liberdade para corrigir a base até o limite em que ela continue representando uma operação possível e coerente.

### Cálculos monetários e custo

O sistema utilizará o real como moeda e registrará valores monetários com duas casas decimais.

- total de um item = quantidade × valor unitário;
- total da compra = soma dos totais dos itens comprados;
- total da venda = soma dos totais dos itens pelos preços praticados;
- saldo da venda = total da venda − pagamentos recebidos;
- cada pagamento deve ser maior que zero e não pode superar o saldo existente;
- diferença comercial = total pelos preços de referência − total pelos preços praticados;
- diferença positiva representa desconto; diferença negativa representa venda acima da referência.

Entradas por compra atualizarão o custo médio ponderado da variante. A venda preservará o custo médio vigente no momento em que for confirmada, de modo que alterações futuras não modifiquem o custo histórico da venda.

Uma entrada por ajuste utilizará o custo atual da variante. Se ainda não houver custo, será necessário informá-lo. Correções e anulações recalcularão os valores afetados sem alterar silenciosamente os registros históricos.

O registro da compra controlará, nesta fase, os itens, custos e valor total, mas não pagamentos feitos ao fornecedor. O controle financeiro estruturado permanecerá restrito aos recebimentos vinculados às vendas. Um eventual controle de pagamentos de compras dependerá de nova decisão baseada em necessidade real.

### Cadastros auxiliares

Fornecedores terão cadastro próprio, reutilizável e editável, com nome obrigatório e único após normalização. Informações adicionais serão opcionais.

Categorias, canais e formas de pagamento serão cadastros simples baseados em nome, sem hierarquias, regras ou fluxos próprios. Esses cadastros poderão ser renomeados ou desativados. Um registro já utilizado no histórico não poderá ser apagado; quando desativado, continuará aparecendo nos registros anteriores e deixará de ser oferecido em novas operações.

O histórico preservará os nomes anteriores quando houver renomeação. Duplicidades exatas serão impedidas após a mesma normalização utilizada no catálogo; nomes apenas semelhantes poderão coexistir após decisão do dono.

### Rastreabilidade

O sistema preservará:

- data e hora de criação;
- data e hora de cada alteração;
- versões anteriores de compras, vendas, pagamentos, inventário e ajustes;
- campos alterados, valores anteriores e valores novos;
- motivo de correções e anulações;
- vínculo de cada movimentação de estoque com inventário, compra, venda ou ajuste manual.

Como existe apenas um usuário, não será criada uma estrutura adicional de autoria, papéis ou aprovações. O histórico registrará a ação como realizada pelo dono autenticado.

### Limites operacionais destas regras

Ficam fora do escopo inicial:

- despesas;
- caixa e contas bancárias;
- frete;
- comissões;
- impostos;
- emissão fiscal;
- contas financeiras genéricas;
- conciliação bancária;
- fluxo de caixa;
- transferências;
- pagamentos ou recebimentos sem vínculo com uma compra ou venda.

O sistema não será um controle financeiro geral. Nesta fase, preservará os custos e totais das compras e controlará somente os pagamentos recebidos vinculados às vendas.

---

## Informação gerencial

### Objetivo da informação gerencial

O LGD Mantos deverá transformar os registros operacionais em uma visão clara da situação da loja, identificar o que merece atenção, explicar as evidências e sugerir caminhos possíveis. Seu papel é ajudar o dono a compreender o que está acontecendo e tomar decisões sobre estoque, compras, preços, vendas e recebimentos.

O sistema não será apenas um painel de números e não decidirá ou executará ações comerciais automaticamente. Toda recomendação deverá manter a decisão final com o dono e permitir a consulta dos dados que a sustentam.

As necessidades gerenciais confirmadas são:

- decidir o que comprar e em que quantidade;
- reconhecer características com melhor ou pior saída;
- identificar produtos parados;
- avaliar os preços praticados e a margem realizada;
- acompanhar valores vendidos, recebidos e pendentes;
- compreender o valor mantido em estoque;
- avaliar os canais utilizados;
- relacionar fornecedores e compras aos resultados posteriores dos produtos adquiridos.

Como a frequência e o valor de cada consulta somente poderão ser conhecidos após o uso real, o produto não imporá uma prioridade fixa entre os temas. A navegação deverá manter as informações claras e separadas, permitindo que a evolução posterior seja orientada pelo uso observado.

### Organização das visões

A informação gerencial será separada em uma visão geral e cinco visões especializadas. Essa separação deverá evitar a concentração de todos os números em uma única tela e permitir que o dono avance do resumo para as evidências detalhadas.

#### Visão geral

A entrada gerencial apresentará um resumo da situação atual, sem substituir as visões especializadas. Ela reunirá:

- situação atual do estoque;
- vendas registradas;
- valores recebidos e pendentes;
- margem bruta realizada;
- principais pontos de atenção;
- acesso direto à visão que explica cada informação.

Não haverá obrigação de destacar permanentemente um tema acima dos demais. A organização e a clareza terão prioridade sobre a quantidade de indicadores exibidos.

#### Estoque e giro

Esta visão deverá mostrar:

- itens e quantidades disponíveis;
- produtos que ainda não venderam, venderam parcialmente ou se esgotaram;
- tempo de permanência de cada produto no estoque;
- tempo desde a última venda;
- quantidade atual e quantidade vendida;
- valor do estoque pelo custo médio;
- características com maior e menor saída.

Um produto merecerá atenção pela combinação entre tempo sem venda, quantidade disponível e valor mantido em estoque. O sistema não adotará inicialmente um prazo arbitrário para classificar um produto como encalhado. Em vez disso, permitirá ordenar e analisar os itens pelas evidências disponíveis.

O giro não será interpretado como necessidade de recomprar a mesma estampa. As análises deverão reconhecer que uma estampa específica raramente é reposta e utilizar o comportamento de marca, modelo, categoria, tamanho e cor para apoiar compras futuras.

#### Vendas e margens

Esta visão deverá mostrar:

- quantidade e valor vendidos;
- custo histórico dos itens vendidos;
- resultado bruto;
- margem bruta realizada;
- preços de referência e preços praticados;
- descontos e vendas acima da referência;
- vendas por canal;
- desempenho por produto e variante;
- desempenho agregado por marca, modelo, categoria, tamanho e cor.

A margem será informativa. O sistema não imporá margem mínima nem bloqueará uma negociação com base nela.

Como despesas, impostos, comissões e caixa não são controlados, o sistema utilizará **resultado bruto** e **margem bruta realizada**. Ele não apresentará esses valores como lucro líquido.

#### Recebimentos

Esta visão deverá separar:

- valor total vendido;
- valor recebido;
- saldo pendente;
- vendas pendentes;
- pagamentos registrados em cada venda.

Ela apoiará o acompanhamento financeiro das vendas, sem se transformar em agenda de cobrança e sem agrupar valores por cliente.

#### Compras e fornecedores

Esta visão deverá permitir analisar:

- compras realizadas;
- quantidades e valores comprados;
- fornecedores utilizados;
- características compradas;
- relação entre o que foi comprado, vendido e ainda permanece no estoque;
- resultados posteriores dos produtos adquiridos de cada fornecedor.

O sistema poderá apresentar evidências relacionadas aos fornecedores, mas não deverá afirmar que um fornecedor é melhor quando não houver dados suficientes para essa conclusão.

#### Apoio à próxima compra

As recomendações não deverão pressupor a recompra da mesma estampa. Elas poderão indicar:

- características com evidência de boa saída;
- tamanhos e cores com maior procura;
- marcas, modelos e categorias com melhor desempenho;
- características presentes em produtos parados;
- lacunas percebidas na composição atual do estoque;
- quantidades sugeridas para combinações relevantes.

Toda sugestão deverá apresentar os dados que a sustentam, incluindo quantidade vendida, estoque atual, tempo observado e margem realizada. Também deverá indicar sua confiança ou informar que os dados ainda são insuficientes.

As quantidades sugeridas deverão ser conservadoras e baseadas exclusivamente no comportamento registrado. Quando não houver histórico suficiente, o sistema não produzirá uma recomendação numérica artificial. Nenhuma sugestão criará uma compra ou modificará o estoque automaticamente.

### Tratamento do tempo nas consultas

O estado atual do estoque será apresentado sem depender de um período. Análises históricas utilizarão, por padrão, todo o histórico confiável desde o início do controle.

Quando uma decisão exigir um recorte temporal, o dono poderá definir diretamente um intervalo de datas. O produto não oferecerá atalhos predefinidos como últimos dias, mês atual ou períodos semelhantes, não imporá ciclos fixos de acompanhamento e não exigirá comparação com um período anterior.

O intervalo servirá somente como filtro de consulta. Ele não criará metas, fechamentos, estados ou rotinas adicionais.

### Valor mantido no estoque

O valor do estoque será calculado pela soma das quantidades disponíveis multiplicadas pelo custo médio de cada variante. Essa informação ficará na visão de estoque e servirá para identificar valor concentrado em produtos parados, sem receber destaque obrigatório na visão geral.

O valor potencial de venda do estoque não será adotado nesta fase, pois poderia ser interpretado incorretamente como dinheiro disponível ou resultado garantido.

### Indicadores necessários

As visões utilizarão somente os indicadores necessários às decisões confirmadas:

- quantidade disponível;
- quantidade vendida;
- tempo no estoque;
- tempo desde a última venda;
- valor do estoque pelo custo médio;
- valor vendido;
- valor recebido;
- saldo pendente;
- custo histórico dos itens vendidos;
- resultado bruto;
- margem bruta realizada;
- diferença entre preço de referência e preço praticado.

Não será criado um indicador abstrato ou uma nota geral de “saúde da loja”. A situação deverá ser compreendida pelas evidências separadas, sem esconder contextos diferentes em uma única classificação.

### Responsabilidades

O sistema será responsável por:

- calcular informações a partir dos registros operacionais confiáveis;
- separar situação atual, histórico, análise e recomendação;
- explicar a origem de pontos de atenção e sugestões;
- informar quando não houver dados suficientes;
- permitir chegar de um indicador aos registros que o formaram;
- preservar os registros de origem sem alterações silenciosas.

O dono continuará responsável por:

- interpretar o contexto da loja;
- decidir o que e quanto comprar;
- definir e negociar preços;
- aceitar, adaptar ou ignorar recomendações;
- executar qualquer ação comercial.

### Limites da informação gerencial

Ficam removidos do escopo atual:

- DRE;
- ponto de equilíbrio;
- lucro líquido;
- projeção e controle de caixa;
- metas automáticas;
- orçamento;
- previsão financeira;
- avaliação contábil;
- decisões, compras ou alterações automáticas baseadas em recomendações.

Esses conceitos não deverão ser simulados com dados incompletos. Somente poderão retornar à descoberta caso surja uma necessidade real acompanhada das informações necessárias para sustentá-los.

---

## Disponibilização de dados para usos externos

### Papel do produto

O LGD Mantos não terá uma camada ou domínio de marketing. Sua responsabilidade será manter dados operacionais e gerenciais corretos, coerentes, rastreáveis e reutilizáveis, de forma que possam futuramente servir a ferramentas, sistemas ou processos externos responsáveis pelo marketing da loja.

O uso dos dados por uma atividade externa não transforma essa atividade em responsabilidade do LGD Mantos. A responsabilidade do produto termina na disponibilização segura e coerente dos dados; seleção de produtos, estratégia, criação de conteúdo, produção de artes, aprovação editorial, publicação e medição de campanhas pertencem ao meio externo.

### Separação entre dados e interpretação externa

Os registros do LGD Mantos continuarão sendo a fonte dos fatos sobre produtos, variantes, preços de referência, estoque, compras, vendas e análises gerenciais já validadas. Ferramentas externas poderão consultar e transformar os dados disponibilizados, mas suas interpretações, recomendações e conteúdos não passarão automaticamente a compor o registro operacional do sistema.

A disponibilização será somente de leitura em relação à base controlada pelo LGD Mantos. Uma integração externa não poderá criar ou alterar catálogo, estoque, preços, compras, vendas ou outros registros operacionais sem uma nova decisão de produto que defina essa responsabilidade e suas regras de consistência.

Dados internos não serão expostos automaticamente apenas porque existem. Quando surgir um uso externo real, deverão ser definidos os dados estritamente necessários para ele, preservando a separação entre informações comerciais reutilizáveis e informações internas, como custos, margens, fornecedores, recebimentos e saldos pendentes.

### Preparação para reutilização futura

Estar preparado para reutilização e integração significa preservar qualidade, organização, rastreabilidade e separação de responsabilidades nos dados. Isso é um princípio do produto, e não uma obrigação de implementar antecipadamente uma API, exportação genérica, conector ou arquitetura adicional.

Não será definido nesta fase se a disponibilização ocorrerá por consulta, relatório, arquivo, API ou integração direta. Também não serão escolhidos provedor de inteligência artificial, rede social ou ferramenta de marketing. Dados específicos, formato, frequência, permissões e fluxo serão decididos somente quando existir uma necessidade externa real.

### Capacidades removidas ou adiadas

Ficam removidos do escopo atual:

- campanhas de marketing assistidas;
- criação ou armazenamento de textos, artes e outros materiais promocionais;
- aprovação e fila de publicação;
- calendário editorial, agendamento e estados de publicação;
- publicação direta em redes sociais;
- indicadores próprios de campanha, alcance, engajamento, conversão ou atribuição de vendas ao marketing.

Ficam adiadas até que exista uma necessidade externa concreta:

- definição do meio de disponibilização dos dados;
- integração com ferramentas de marketing, redes sociais ou provedores de inteligência artificial;
- definição de formatos, permissões, frequência e conjunto de dados de cada integração.

---

## Fronteiras do produto

### Acesso e administração

O produto terá um único acesso, destinado ao dono. A autenticação e a administração serão limitadas à proteção desse acesso e às configurações indispensáveis ao uso do sistema. Gestão de equipe, múltiplos usuários, papéis, permissões e estruturas administrativas adicionais não pertencem ao escopo atual.

### Cadastros e sinalizações de apoio

Fornecedores, categorias, canais e formas de pagamento são cadastros auxiliares dos módulos e responsabilidades principais. Eles não terão processos, hierarquias ou módulos independentes além das regras já definidas.

O sistema poderá apresentar sinalizações internas relacionadas à operação, à gestão e à qualidade dos dados. Notificações por e-mail, WhatsApp ou outros meios externos não pertencem ao escopo atual.

### Fotos dos produtos

O controle de fotos dos produtos pertence ao LGD Mantos porque resolve uma dificuldade atual de armazenamento, identificação e disponibilidade das imagens, melhora o controle visual do estoque e preserva um dado que poderá ser reutilizado futuramente por serviços externos.

As regras serão:

- um produto poderá possuir várias fotos;
- as fotos pertencerão primariamente ao produto;
- uma foto poderá ser associada opcionalmente a uma cor ou variante quando representar uma diferença visual relevante;
- não será exigida uma foto para cada tamanho, cor ou variante;
- uma foto poderá ser definida como principal;
- o cadastro de fotos será opcional e não impedirá inventário, compra ou venda;
- as fotos poderão ser adicionadas, visualizadas, ordenadas, substituídas e removidas;
- as fotos poderão futuramente ser reutilizadas por serviços externos junto aos demais dados do produto.

O sistema não fará aprovação editorial, tratamento, edição ou geração de imagens, classificação de fotos para marketing ou publicação. Comprovantes, notas, recibos e quaisquer outros documentos, anexos, arquivos ou imagens não pertencem ao escopo atual.

### Consultas, relatórios e arquivos

As informações operacionais e analíticas serão consultadas diretamente nas visões do sistema. Impressão, geração de arquivos e produção de relatórios exportáveis ou documentos formatados não pertencem ao escopo atual.

Nenhum meio de disponibilização externa será implementado antecipadamente. Exportações, APIs e conectores somente poderão ser definidos quando existir um consumidor real e uma necessidade concreta.

### Qualidade e manutenção dos dados

Pertencem ao produto as validações necessárias à consistência dos registros e os alertas internos, claros e explicáveis, sobre dados ausentes, duplicados ou potencialmente inconsistentes. Sempre que aplicável, o alerta deverá permitir identificar os registros que o originaram, e a decisão sobre a correção continuará com o dono.

Um alerta informativo de qualidade não bloqueará uma operação. Somente as regras de consistência já validadas poderão impedir seu registro. O produto não criará uma nota abstrata de qualidade da base.

Não pertencem ao produto a limpeza automática, a fusão automática de cadastros, a correção silenciosa, o enriquecimento por fontes externas ou a alteração de registros baseada apenas em sugestões.

### Backup, recuperação e disponibilidade

Backup, retenção, restauração, recuperação e disponibilidade serão tratados posteriormente como requisitos técnicos e operacionais da infraestrutura. Eles não formarão um módulo ou fluxo de negócio do LGD Mantos. Exportar dados não será apresentado como mecanismo de backup.

### Automações e integrações

Nenhuma integração, sincronização ou automação externa pertence ao escopo inicial. Sua inclusão futura exigirá um caso real, um consumidor ou responsável identificado e um benefício comprovado. Antes de qualquer inclusão, também deverão ser definidos os dados envolvidos, a direção do fluxo, a autoridade para alterações e o tratamento de falhas.

Esse limite não remove os comportamentos internos e determinísticos necessários às regras já validadas, como calcular totais e saldos, atualizar o estoque, recalcular correções, gerar códigos internos e produzir análises e recomendações explicáveis.

---

## Prioridades do produto

### Critério de priorização

A prioridade será determinada pelo valor necessário para tornar o LGD Mantos a fonte confiável da operação da loja. Dependências reais prevalecerão sobre a quantidade de funcionalidades: primeiro o sistema deverá registrar corretamente os acontecimentos e preservar sua consistência; depois deverá transformar o histórico confiável em apoio gerencial; capacidades externas somente serão consideradas quando houver uma necessidade concreta.

Prioridade não significa criar versões incompletas das regras. Toda capacidade incluída deverá respeitar desde o início as validações, os cálculos e a rastreabilidade que sustentam sua consistência.

### Núcleo obrigatório para o início do uso real

O núcleo obrigatório será composto pelas capacidades necessárias para substituir a ausência atual de controle e formar uma base confiável:

1. **Acesso e estrutura básica:** acesso único do dono e configurações indispensáveis ao uso.
2. **Catálogo:** produtos, variantes, códigos internos, marcas, modelos, categorias, tamanhos, cores, custos e preços de referência.
3. **Fotos dos produtos:** várias fotos por produto, uma principal e associação opcional a cor ou variante.
4. **Cadastros auxiliares:** fornecedores, canais de compra e venda e formas de pagamento, sem processos próprios.
5. **Inventário inicial:** formação única do ponto zero com os dados conhecidos, sem inventar informações ausentes.
6. **Compras:** registro direto das aquisições e de seus efeitos no estoque e no custo médio.
7. **Estoque:** quantidade disponível, movimentações vinculadas às origens e ajustes manuais justificados.
8. **Vendas e recebimentos:** registro direto da venda, baixa de estoque, preços praticados, pagamentos, saldo e situação financeira.
9. **Correções e rastreabilidade:** edição segura, anulação, versões anteriores, motivos e proibição de estoque negativo ou inconsistências financeiras.
10. **Consultas operacionais mínimas:** estoque atual, histórico de compras, vendas, movimentações, valores vendidos, recebidos e pendentes.

Validações obrigatórias de consistência fazem parte de cada capacidade do núcleo e não constituem uma entrega separada ou opcional.

### Evolução gerencial após a base confiável

Depois que o núcleo estiver em uso e produzindo histórico confiável, a prioridade seguinte será completar as visões gerenciais já definidas:

1. visão geral da situação da loja;
2. estoque e giro;
3. vendas e margens;
4. recebimentos;
5. compras e fornecedores;
6. apoio à próxima compra;
7. alertas internos e explicáveis de qualidade dos dados.

Essa ordem organiza dependências e não impõe frequência de consulta. Indicadores derivados, pontos de atenção e recomendações somente deverão ser apresentados quando seus registros de origem existirem e forem suficientes. O sistema deverá reconhecer a insuficiência de dados em vez de produzir conclusões artificiais.

### Preparação externa sem implementação antecipada

A organização, a rastreabilidade e a qualidade dos dados deverão ser preservadas em todas as etapas para permitir reutilização futura. Isso não cria uma entrega própria de exportação ou integração.

Relatórios exportáveis, geração de arquivos, APIs, conectores, integrações, sincronizações, inteligência artificial externa e publicação em outros serviços não serão implementados enquanto não existirem consumidor real, finalidade definida, dados necessários, responsável e benefício comprovado.

### Itens explicitamente fora do escopo atual

Não fazem parte do produto atual:

- cadastro ou gestão de clientes;
- gestão de equipe, múltiplos usuários, papéis ou permissões;
- empréstimo, demonstração, transporte, entrega ou localização de peças;
- troca, devolução, defeito e demais processos de pós-venda;
- despesas, contas bancárias, caixa, fluxo de caixa e conciliação;
- pagamentos a fornecedores e contas financeiras genéricas;
- frete, comissões, impostos e emissão fiscal;
- DRE, lucro líquido, ponto de equilíbrio, orçamento, metas e previsões financeiras;
- loja física, comércio eletrônico ou atendimento comercial;
- marketing, campanhas, conteúdo, aprovação editorial, calendário e publicação;
- impressão, geração de documentos e relatórios exportáveis;
- notificações externas;
- anexos e arquivos diferentes das fotos dos produtos;
- tratamento, edição ou geração de imagens;
- limpeza, fusão, correção ou enriquecimento automático de dados;
- integrações, sincronizações ou automações externas sem necessidade validada;
- operação multiempresa ou generalização para comercialização do sistema.

Itens fora do escopo não constituem uma lista de funcionalidades futuras. Eles somente poderão retornar à descoberta diante de uma necessidade real que justifique rever a fronteira do produto.

### Resultado observável e rotina essencial

O LGD Mantos será considerado a central da loja quando:

- o inventário inicial representar o estoque físico conhecido;
- toda nova compra, venda, pagamento e correção for registrada no sistema;
- a quantidade disponível puder ser consultada sem uma nova contagem completa;
- os valores vendidos, recebidos e pendentes puderem ser conhecidos pelos registros;
- o dono conseguir consultar o histórico e compreender a origem das informações sem recorrer a controles paralelos como fonte principal.

A rotina essencial será registrar cada acontecimento operacional quando ele ocorrer e consultar o sistema antes de decidir com base em estoque, compras, vendas ou recebimentos. O produto não imporá uma rotina diária, semanal ou mensal artificial.

---

## Princípios do produto

Os princípios abaixo foram confirmados ou decorrem diretamente das decisões desta rodada:

1. **Uma única fonte de verdade:** o registro operacional deve ser confiável e rastreável.
2. **Consistência antes de conveniência:** nenhuma facilidade deve permitir estoque negativo ou quebrar o histórico da operação.
3. **Decisão humana nas ações sensíveis:** automações podem recomendar, mas não devem assumir decisões comerciais sem autorização.
4. **Separação de responsabilidades:** marketing e análises consomem dados operacionais sem reescrevê-los.
5. **Escopo explícito:** uma necessidade da loja não passa automaticamente a ser responsabilidade do sistema.
6. **Evolução orientada ao negócio:** tecnologia só deve ser escolhida depois de problema, regra, responsável e resultado esperado estarem claros.
7. **Simplicidade para um único responsável:** a organização do produto deve favorecer a visão integrada do dono e evitar camadas desnecessárias de complexidade.
8. **Dados como ativo reutilizável:** os registros devem ter qualidade suficiente para alimentar análises, integrações e fluxos externos.
9. **Ferramenta certa para cada responsabilidade:** fornecer dados a uma atividade externa não obriga o LGD Mantos a executar essa atividade.
10. **Produto interno antes de solução genérica:** decisões atuais devem atender à LGD Mantos, sem complexidade criada para uma comercialização hipotética.
11. **Complexidade proporcional ao valor:** o produto não deve modelar todos os casos possíveis; somente serão incluídos estados, regras e processos necessários ao controle real ou que produzam valor claro para a loja.
