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
