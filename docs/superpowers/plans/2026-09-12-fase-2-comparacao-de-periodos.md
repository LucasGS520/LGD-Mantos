# Fase 2 — Comparação de Períodos: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Todo indicador relevante da aba Inteligência passa a mostrar quanto variou em relação ao período anterior.

**Architecture:** Uma função pura resolve o par de janelas (atual, anterior) a partir do mesmo vocabulário de período que a aplicação já usa. Um value object carrega os dois valores e a variação juntos. Os services de analytics ganham um parâmetro opcional `compare`; quando ele é falso, o comportamento atual não muda em nada. O frontend renderiza a variação ao lado do número.

**Tech Stack:** FastAPI · SQLAlchemy 2.0 async · PostgreSQL 16 · pytest (`asyncio_mode = auto`) · React 18 + TypeScript + Vite.

**Spec:** `docs/superpowers/specs/2026-09-10-reformulacao-inteligencia-lgd-design.md`, seção 3.6

## Global Constraints

- Comentários e docstrings **sempre em português (PT-BR)**, explicativos e voltados à manutenção.
- **Nenhum endpoint novo.** Os endpoints existentes ganham um parâmetro; nenhuma rota nasce.
- **Compatibilidade retroativa obrigatória:** sem `compare=true`, toda resposta continua idêntica byte a byte à de hoje. Os 45 testes existentes são a prova disso e não podem ser alterados para acomodar a mudança.
- **Nenhuma alteração no módulo Operacional** (`backend/app/modules/operational/`) nem nas telas `screens/op/` e `screens/mais/`.
- Não introduzir a camada `intelligence/` — ela é da Fase 3. Esta fase mexe só em `analytics/` e no frontend.
- Toda verificação exige evidência real: comando executado e saída.
- Não fazer `git push`. Não rodar `graphify update` (uma vez só, na Task 4).
- Migration head atual: `0005`. Esta fase **não cria migration** — nada muda no schema.

## Decisão de produto que governa a fase

O responsável pelo produto decidiu em 2026-09-12: **o mês corrente é comparado contra os mesmos dias decorridos do mês anterior**, não contra o mês anterior inteiro.

Motivo: no dia 12, comparar contra um mês fechado faria a receita parecer despencar por artefato de calendário, não por desempenho. A comparação precisa ser justa em qualquer dia do mês.

Consequência nas bordas: quando o mês corrente é mais longo que o anterior (dia 31 contra um mês de 30 dias), a janela anterior é limitada ao fim do próprio mês anterior. Na prática, compara-se até onde o mês anterior existiu.

---

## Task 1: As primitivas de comparação

**Files:**
- Modify: `backend/app/modules/analytics/utils.py`
- Create: `backend/app/modules/analytics/schemas/comparacao.py`
- Create: `backend/tests/test_comparacao_de_periodos.py`

**Interfaces:**
- Consumes: `resolve_period(period, days)`, que já existe em `utils.py` e não muda.
- Produces: `resolve_comparison_period(period, days) -> (atual, anterior)`, onde cada elemento é `(start, end)`; e `Comparado`, com os campos `atual: float`, `anterior: float | None`, `variacao_pct: float | None`. A Task 2 consome os dois.

Esta task é 100% função pura, sem banco. É o melhor alvo de TDD da fase — escreva os testes antes.

- [ ] **Step 1: Escrever os testes primeiro**

Criar `backend/tests/test_comparacao_de_periodos.py`:

```python
"""Resolução do par (período atual, período anterior) e cálculo de variação.

Funções puras, sem banco. As bordas que importam são as viradas de mês e de ano,
e o caso em que o mês anterior é mais curto que o corrente.
"""

from datetime import datetime, timezone

import pytest

from app.modules.analytics.schemas.comparacao import Comparado
from app.modules.analytics.utils import resolve_comparison_period


def _em(ano: int, mes: int, dia: int, hora: int = 12) -> datetime:
    return datetime(ano, mes, dia, hora, tzinfo=timezone.utc)


class TestMesCorrente:
    def test_compara_contra_os_mesmos_dias_decorridos(self):
        agora = _em(2026, 9, 12)
        (ini_atual, fim_atual), (ini_ant, fim_ant) = resolve_comparison_period(
            "current_month", agora=agora
        )
        assert ini_atual == _em(2026, 9, 1, 0)
        assert fim_atual == agora
        assert ini_ant == _em(2026, 8, 1, 0)
        # 11 dias e 12 horas decorridos em setembro → mesma janela em agosto.
        assert fim_ant == _em(2026, 8, 12)

    def test_mes_anterior_mais_curto_limita_a_janela(self):
        # 31 de março: março tem 31 dias, fevereiro de 2026 tem 28. A janela
        # anterior não pode invadir março — para no fim de fevereiro.
        agora = _em(2026, 3, 31)
        _, (ini_ant, fim_ant) = resolve_comparison_period("current_month", agora=agora)
        assert ini_ant == _em(2026, 2, 1, 0)
        assert fim_ant == _em(2026, 3, 1, 0)

    def test_virada_de_ano(self):
        agora = _em(2026, 1, 10)
        _, (ini_ant, fim_ant) = resolve_comparison_period("current_month", agora=agora)
        assert ini_ant == _em(2025, 12, 1, 0)
        assert fim_ant == _em(2025, 12, 10)


class TestMesAnterior:
    def test_compara_dois_meses_fechados(self):
        agora = _em(2026, 9, 12)
        (ini_atual, fim_atual), (ini_ant, fim_ant) = resolve_comparison_period(
            "last_month", agora=agora
        )
        assert ini_atual == _em(2026, 8, 1, 0)
        assert fim_atual == _em(2026, 9, 1, 0)
        assert ini_ant == _em(2026, 7, 1, 0)
        assert fim_ant == _em(2026, 8, 1, 0)


class TestJanelasMoveis:
    @pytest.mark.parametrize("period,dias", [("last_3_months", 90), ("last_6_months", 180)])
    def test_janela_anterior_tem_o_mesmo_tamanho(self, period, dias):
        agora = _em(2026, 9, 12)
        (ini_atual, fim_atual), (ini_ant, fim_ant) = resolve_comparison_period(
            period, agora=agora
        )
        assert (fim_atual - ini_atual).days == dias
        assert (fim_ant - ini_ant).days == dias
        assert fim_ant == ini_atual

    def test_fallback_em_dias_usa_a_janela_imediatamente_anterior(self):
        agora = _em(2026, 9, 12)
        (ini_atual, fim_atual), (ini_ant, fim_ant) = resolve_comparison_period(
            None, days=7, agora=agora
        )
        assert (fim_atual - ini_atual).days == 7
        assert (fim_ant - ini_ant).days == 7
        assert fim_ant == ini_atual


class TestAnoCorrente:
    def test_compara_contra_o_mesmo_periodo_do_ano_passado(self):
        agora = _em(2026, 3, 15)
        (ini_atual, _), (ini_ant, fim_ant) = resolve_comparison_period(
            "current_year", agora=agora
        )
        assert ini_atual == _em(2026, 1, 1, 0)
        assert ini_ant == _em(2025, 1, 1, 0)
        assert fim_ant == _em(2025, 3, 15)


class TestComparado:
    def test_calcula_variacao_percentual(self):
        c = Comparado.de(atual=18200.0, anterior=16350.0)
        assert c.atual == 18200.0
        assert c.anterior == 16350.0
        assert c.variacao_pct == 11.3

    def test_queda_gera_variacao_negativa(self):
        c = Comparado.de(atual=4230.0, anterior=4539.0)
        assert c.variacao_pct == -6.8

    def test_anterior_zero_nao_gera_variacao(self):
        # Dividir por zero produziria infinito; "+∞%" não informa nada ao operador.
        c = Comparado.de(atual=500.0, anterior=0.0)
        assert c.variacao_pct is None

    def test_anterior_ausente_nao_gera_variacao(self):
        c = Comparado.de(atual=500.0, anterior=None)
        assert c.variacao_pct is None

    def test_ambos_zero_nao_gera_variacao(self):
        c = Comparado.de(atual=0.0, anterior=0.0)
        assert c.variacao_pct is None
```

- [ ] **Step 2: Rodar e confirmar que falha**

```bash
cd backend && pytest tests/test_comparacao_de_periodos.py -v
```

Esperado: erro de import — `resolve_comparison_period` e `Comparado` ainda não existem. Cole a saída.

- [ ] **Step 3: Criar o value object**

`backend/app/modules/analytics/schemas/comparacao.py`:

```python
"""Value object que carrega um indicador junto com seu valor no período anterior."""

from pydantic import BaseModel


class Comparado(BaseModel):
    """Um número, o mesmo número no período anterior, e a variação entre eles.

    `variacao_pct` é None sempre que a comparação não faz sentido — anterior
    ausente ou zero. Exibir "+∞%" ou "+100%" nesses casos daria ao operador uma
    falsa sensação de tendência onde não há base de comparação.
    """

    atual: float
    anterior: float | None = None
    variacao_pct: float | None = None

    @classmethod
    def de(cls, atual: float, anterior: float | None) -> "Comparado":
        """Monta o objeto já calculando a variação percentual."""
        if anterior is None or anterior == 0:
            return cls(atual=atual, anterior=anterior, variacao_pct=None)
        variacao = (atual - anterior) / anterior * 100
        return cls(atual=atual, anterior=anterior, variacao_pct=round(variacao, 1))
```

- [ ] **Step 4: Implementar `resolve_comparison_period`**

Acrescentar ao final de `backend/app/modules/analytics/utils.py`:

```python
Janela = tuple[datetime, datetime]


def resolve_comparison_period(
    period: str | None,
    days: int = 30,
    agora: datetime | None = None,
) -> tuple[Janela, Janela]:
    """Retorna (janela_atual, janela_anterior) para o período informado.

    A regra de comparação depende do tipo de período:

    - `current_month` e `current_year` são períodos *em andamento*. A janela
      anterior cobre os mesmos dias decorridos do mês/ano anterior, não o
      período fechado inteiro. Decisão de produto de 2026-09-12: comparar o dia
      12 contra um mês fechado faria a receita parecer despencar por artefato de
      calendário. Quando o período anterior é mais curto (dia 31 contra um mês
      de 30 dias), a janela é limitada ao fim dele.
    - `last_month` já é um período fechado: compara-se contra o mês fechado
      imediatamente anterior.
    - Janelas móveis (`last_3_months`, `last_6_months` e o fallback em dias)
      comparam contra a janela de mesmo tamanho imediatamente anterior.

    O parâmetro `agora` existe para os testes fixarem o instante de referência.
    """
    agora = agora or datetime.now(timezone.utc)

    if period == "current_month":
        inicio_atual = datetime(agora.year, agora.month, 1, tzinfo=timezone.utc)
        inicio_anterior = _mes_anterior(inicio_atual)
        decorrido = agora - inicio_atual
        # O min() impede que a janela anterior invada o mês corrente quando o
        # mês anterior tem menos dias do que já se passaram neste.
        fim_anterior = min(inicio_anterior + decorrido, inicio_atual)
        return (inicio_atual, agora), (inicio_anterior, fim_anterior)

    if period == "current_year":
        inicio_atual = datetime(agora.year, 1, 1, tzinfo=timezone.utc)
        inicio_anterior = datetime(agora.year - 1, 1, 1, tzinfo=timezone.utc)
        decorrido = agora - inicio_atual
        fim_anterior = min(inicio_anterior + decorrido, inicio_atual)
        return (inicio_atual, agora), (inicio_anterior, fim_anterior)

    if period == "last_month":
        inicio_deste = datetime(agora.year, agora.month, 1, tzinfo=timezone.utc)
        inicio_atual = _mes_anterior(inicio_deste)
        inicio_anterior = _mes_anterior(inicio_atual)
        return (inicio_atual, inicio_deste), (inicio_anterior, inicio_atual)

    # Janelas móveis: o período anterior é do mesmo tamanho, colado ao atual.
    inicio_atual, fim_atual = resolve_period(period, days)
    tamanho = fim_atual - inicio_atual
    return (inicio_atual, fim_atual), (inicio_atual - tamanho, inicio_atual)


def _mes_anterior(primeiro_dia: datetime) -> datetime:
    """Primeiro instante do mês imediatamente anterior ao informado."""
    ultimo_instante_anterior = primeiro_dia - timedelta(microseconds=1)
    return datetime(
        ultimo_instante_anterior.year,
        ultimo_instante_anterior.month,
        1,
        tzinfo=timezone.utc,
    )
```

- [ ] **Step 5: Rodar e confirmar que passa**

```bash
cd backend && pytest tests/test_comparacao_de_periodos.py -v && pytest -q
```

Esperado: todos os novos verdes, e os 45 anteriores intactos. Cole as duas saídas.

- [ ] **Step 6: Commit**

```bash
git add backend/app/modules/analytics/utils.py backend/app/modules/analytics/schemas/comparacao.py backend/tests/test_comparacao_de_periodos.py
git commit -m "feat(analytics): resolucao de periodo comparativo e value object Comparado"
```

---

## Task 2: Services expõem comparação

**Files:**
- Modify: `backend/app/modules/analytics/services/dashboard_service.py`
- Modify: `backend/app/modules/analytics/services/product_analysis_service.py`
- Modify: `backend/app/modules/analytics/services/channel_analysis_service.py`
- Modify: `backend/app/modules/analytics/services/finance_service.py`
- Modify: `backend/app/modules/analytics/routes/dashboard.py`, `products.py`, `channels.py`, `finance.py`
- Modify: `backend/tests/test_analytics_contracts.py`

**Interfaces:**
- Consumes: `resolve_comparison_period` e `Comparado` da Task 1.
- Produces: cada endpoint aceita `?compare=true`. Com ele, a resposta ganha uma chave `comparacao` — um objeto cujos campos são os mesmos indicadores do payload, cada um no formato `Comparado`. **Sem `compare=true`, a resposta é idêntica à de hoje.** A Task 3 consome essa chave.

Por que uma chave separada em vez de trocar os campos por objetos: os 45 testes existentes e todas as telas atuais leem `data.month_revenue` como número. Aninhar sob `comparacao` mantém tudo funcionando e torna a adoção incremental.

- [ ] **Step 1: `DashboardService` aceita comparação**

`dashboard()` hoje tem a assinatura `dashboard(db)` e fixa o mês corrente internamente. Passa a `dashboard(db, compare: bool = False)`.

Quando `compare` é verdadeiro, calcular os mesmos indicadores para a janela anterior devolvida por `resolve_comparison_period("current_month")` e devolver, além de tudo que já devolve:

```python
"comparacao": {
    "month_revenue": Comparado.de(receita_atual, receita_anterior).model_dump(),
    "gross_profit": Comparado.de(lucro_bruto_atual, lucro_bruto_anterior).model_dump(),
    "net_profit": Comparado.de(lucro_liquido_atual, lucro_liquido_anterior).model_dump(),
    "margin_pct": Comparado.de(margem_atual, margem_anterior).model_dump(),
    "avg_ticket": Comparado.de(ticket_atual, ticket_anterior).model_dump(),
    "total_units_sold": Comparado.de(unidades_atual, unidades_anterior).model_dump(),
}
```

Os repositórios já aceitam janelas: `sales_repo.month_revenue(db, inicio)` e irmãos recebem datas. Onde um repositório só aceitar `since`, use a variante que aceita `since` e `end` — `sales_repo.daily_revenue_series` já tem as duas. Se algum repositório não suportar janela fechada, **pare e reporte** em vez de calcular por subtração.

- [ ] **Step 2: Os outros três services aceitam comparação**

`ProductAnalysisService.product_analysis`, `ChannelAnalysisService.sales_by_channel` e `FinanceService.dre` ganham `compare: bool = False` com o mesmo padrão. Os indicadores comparados de cada um:

| Service | Indicadores em `comparacao` |
| --- | --- |
| `product_analysis` | apenas contagens: `rupture_risk` e `stopped` (quantidade de itens, não as listas) |
| `sales_by_channel` | por canal: `revenue`, `qty` |
| `dre` | `revenue`, `cogs`, `gross_profit`, `gross_margin_pct`, `expenses`, `net_profit`, `margin_pct` |

As chaves do DRE acima foram conferidas no `finance_service.py` — são em inglês.
Não comparar `period`, `expenses_by_category`, `break_even` nem `evolution`: os
dois primeiros não são escalares, e os dois últimos já são, por natureza,
projeções sobre o período.

**`dre` não usa `resolve_comparison_period`.** A assinatura dele é
`dre(db, month, year)`, não `period` — o período anterior é o mês calendário
imediatamente antes do informado, com a virada de ano tratada (janeiro compara
contra dezembro do ano anterior). Calcule isso dentro do próprio service.

Confira os nomes reais das chaves dos outros services antes de escrever — não
presuma.

- [ ] **Step 3: As rotas repassam o parâmetro**

Cada rota ganha `compare: bool = Query(False)` e repassa ao service. Exemplo em `dashboard.py`:

```python
@router.get("/dashboard")
async def dashboard(
    compare: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    return await DashboardService.dashboard(db, compare=compare)
```

- [ ] **Step 4: Testes de contrato para o novo parâmetro**

Acrescentar a `backend/tests/test_analytics_contracts.py`:

```python
async def test_dashboard_sem_compare_nao_traz_comparacao(auth_client):
    """Compatibilidade retroativa: o payload padrão não muda de forma."""
    resposta = await auth_client.get("/api/v1/analytics/dashboard")
    assert "comparacao" not in resposta.json()


async def test_dashboard_com_compare_traz_os_indicadores_comparados(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/dashboard?compare=true")
    comparacao = resposta.json()["comparacao"]
    for indicador in (
        "month_revenue", "gross_profit", "net_profit",
        "margin_pct", "avg_ticket", "total_units_sold",
    ):
        assert indicador in comparacao, f"indicador ausente: {indicador}"
        assert set(comparacao[indicador]) == {"atual", "anterior", "variacao_pct"}
```

- [ ] **Step 5: Rodar a suíte inteira**

```bash
cd backend && pytest -q
```

Esperado: verde, com os 45 anteriores intactos. Se algum dos 45 quebrou, a compatibilidade retroativa falhou — **não ajuste o teste antigo**, conserte o service.

- [ ] **Step 6: Commit**

```bash
git add backend/app/modules/analytics backend/tests/test_analytics_contracts.py
git commit -m "feat(analytics): endpoints aceitam compare e devolvem variacao vs periodo anterior"
```

---

## Task 3: As telas mostram a variação

**Files:**
- Modify: `frontend_pwa/src/services/types.ts`
- Modify: `frontend_pwa/src/services/api.ts`
- Modify: `frontend_pwa/src/components/Analytics.tsx`
- Modify: `frontend_pwa/src/screens/intel/Overview.tsx`, `Products.tsx`, `Stock.tsx`, `Finance.tsx`, `Channels.tsx`

**Interfaces:**
- Consumes: a chave `comparacao` produzida pela Task 2.
- Produces: nada consumido por tasks posteriores.

- [ ] **Step 1: Tipos e chamadas**

Em `types.ts`:

```typescript
/** Um indicador com seu valor no período anterior e a variação entre eles.
 *  `variacao_pct` é null quando não há base de comparação (anterior ausente ou zero). */
export interface Comparado {
  atual: number
  anterior: number | null
  variacao_pct: number | null
}
```

E acrescentar `comparacao?: Record<string, Comparado>` às interfaces `Dashboard`, `ProductAnalysis`, `DRE` e à de canais. Campo opcional, porque sem `compare=true` ele não vem.

Em `api.ts`, os getters correspondentes ganham um parâmetro `compare?: boolean` que acrescenta `compare=true` à querystring. Siga o padrão do helper `periodOuDiasQuery` já existente.

- [ ] **Step 2: Um componente para renderizar variação**

Em `components/Analytics.tsx`, acrescentar:

```tsx
/** Mostra a variação percentual de um indicador contra o período anterior.
 *  Verde para alta, vermelho para queda, cinza quando não há base de comparação.
 *  Atenção: para despesas e CMV, alta é ruim — use `inverterCor`. */
export function Variacao({ dado, inverterCor = false }: {
  dado?: Comparado
  inverterCor?: boolean
}) {
  if (!dado || dado.variacao_pct === null || dado.variacao_pct === undefined) {
    return <span style={{ fontSize: 11, color: 'var(--text-4)', fontWeight: 500 }}>sem base anterior</span>
  }
  const subiu = dado.variacao_pct >= 0
  const bom = inverterCor ? !subiu : subiu
  const cor = dado.variacao_pct === 0 ? 'var(--text-3)' : bom ? '#5DD49E' : '#F5847B'
  const sinal = dado.variacao_pct > 0 ? '+' : ''
  return (
    <span className="tnum" style={{ fontSize: 11, fontWeight: 700, color: cor }}>
      {sinal}{dado.variacao_pct.toFixed(1)}%
    </span>
  )
}
```

O `inverterCor` existe porque despesa e CMV subindo é notícia ruim — pintar de verde seria mentir para o operador.

- [ ] **Step 3: Visão Geral**

`Overview.tsx` passa a chamar `api.getDashboard(true)`. Os quatro `KPIInfo` e o bloco de receita do topo ganham `<Variacao dado={data.comparacao?.<indicador>} />` ao lado do valor. Não redesenhe os cards — acrescente o elemento.

- [ ] **Step 4: As outras quatro telas**

Mesmo padrão em `Products.tsx`, `Stock.tsx`, `Finance.tsx` e `Channels.tsx`, nos indicadores que cada uma já exibe. Em `Finance.tsx`, lembrar do `inverterCor` para CMV e despesas.

- [ ] **Step 5: Verificar**

```bash
cd frontend_pwa && npm run build
```

Depois subir (`docker compose up -d`) e percorrer as cinco telas. Confirmar que a variação aparece com dado real, e que indicadores sem base anterior mostram "sem base anterior" em vez de um número inventado.

- [ ] **Step 6: Commit**

```bash
git add frontend_pwa/src
git commit -m "feat(pwa): telas da Inteligencia mostram variacao vs periodo anterior"
```

---

## Task 4: Verificação da fase

Executada direto pelo controlador, sem par implementador e revisor.

- [ ] `cd backend && pytest -q` — verde, contagem maior que os 45 de antes
- [ ] `curl` no dashboard sem `compare` — resposta sem a chave `comparacao`
- [ ] `curl` no dashboard com `compare=true` — os seis indicadores comparados
- [ ] `npm run build` limpo
- [ ] As cinco telas mostram variação com dado real
- [ ] `graphify update .`
- [ ] Commit do grafo

## Verificações que reprovam a fase

- Algum dos 45 testes anteriores quebrou, ou foi alterado para acomodar a mudança.
- Uma resposta sem `compare=true` mudou de forma.
- Alguma tela mostra `+100%` ou `+∞%` onde o período anterior era zero.
- Despesa ou CMV subindo aparece pintado de verde.
