"""Campos compartilhados apenas por inventário e ajustes físicos."""


def validate_stock_event(data):
    if data.payments or data.channel_id or data.supplier_id or data.purchase_date:
        raise ValueError("Inventário/ajuste não recebe campos de compra ou venda")
    if any(item.unit_price is not None for item in data.items):
        raise ValueError("Inventário/ajuste não recebe preço praticado")
