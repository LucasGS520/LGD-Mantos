"""Utilitários de resolução de período para analytics."""

from datetime import datetime, timedelta, timezone


def resolve_period(period: str | None, days: int = 30) -> tuple[datetime, datetime]:
    """Retorna (start, end) em UTC para um período nomeado ou número de dias.

    Períodos nomeados:
    - current_month: do 1º dia do mês atual até agora
    - last_month: mês calendário anterior completo
    - last_3_months: últimos 90 dias até agora
    - last_6_months: últimos 180 dias até agora
    - current_year: de 1º de janeiro do ano atual até agora
    - None / fallback: últimos `days` dias até agora
    """
    now = datetime.now(timezone.utc)
    today = now.date()

    if period == "current_month":
        start = datetime(today.year, today.month, 1, tzinfo=timezone.utc)
        return start, now

    if period == "last_month":
        first_of_this = today.replace(day=1)
        last_of_prev = first_of_this - timedelta(days=1)
        first_of_prev = last_of_prev.replace(day=1)
        return (
            datetime(first_of_prev.year, first_of_prev.month, 1, tzinfo=timezone.utc),
            datetime(first_of_this.year, first_of_this.month, 1, tzinfo=timezone.utc),
        )

    if period == "last_3_months":
        start_date = today - timedelta(days=90)
        return datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc), now

    if period == "last_6_months":
        start_date = today - timedelta(days=180)
        return datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc), now

    if period == "current_year":
        return datetime(today.year, 1, 1, tzinfo=timezone.utc), now

    # Fallback: últimos N dias
    return now - timedelta(days=days), now


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
