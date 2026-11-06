"""Validação específica do acontecimento, sem HTTP ou persistência."""

from .stock_events import validate_stock_event


def validate(data):
    validate_stock_event(data)
    if data.direction:
        raise ValueError("Inventário não recebe direção")
