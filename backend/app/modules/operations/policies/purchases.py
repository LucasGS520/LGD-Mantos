"""Validação específica do acontecimento, sem HTTP ou persistência."""


def validate(data):
    if not data.supplier_id or not data.channel_id:
        raise ValueError("Compra exige fornecedor e canal de compra")
    if data.payments or data.direction:
        raise ValueError("Compra não registra pagamentos ou direção")
    if any(i.unit_cost is None or i.unit_cost <= 0 or i.unit_price is not None for i in data.items):
        raise ValueError("Compra exige custo positivo e não recebe preço praticado")
