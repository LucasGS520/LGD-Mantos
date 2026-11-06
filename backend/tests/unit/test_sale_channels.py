"""Contrato específico de sale_channel."""

import pytest
from app.modules.auxiliaries.sale_channels.schemas import SaleChannelsIn
from pydantic import ValidationError


def test_sale_channels_fixes_kind():
    assert SaleChannelsIn(name="Teste").kind == "sale_channel"
    with pytest.raises(ValidationError):
        SaleChannelsIn(name="Teste", kind="supplier")
