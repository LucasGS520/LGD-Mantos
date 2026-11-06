"""Validação específica do acontecimento, sem HTTP ou persistência."""

from .stock_events import validate_stock_event


def validate(data):
    validate_stock_event(data)
    if not data.direction or not data.reason:
        raise ValueError("Ajuste exige direção e motivo")
