"""Validação específica do acontecimento, sem HTTP ou persistência."""


def validate(data):
    if not data.channel_id or data.supplier_id or data.purchase_date or data.direction:
        raise ValueError("Venda exige canal e não recebe fornecedor, data ou direção")
    if any(
        i.unit_price is None or i.unit_price <= 0 or i.unit_cost is not None for i in data.items
    ):
        raise ValueError("Venda exige preço positivo; custo é obtido pelo servidor")
