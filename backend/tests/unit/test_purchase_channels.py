"""Contrato específico de purchase_channel."""

import pytest
from app.modules.auxiliaries.purchase_channels.schemas import PurchaseChannelsIn
from pydantic import ValidationError


def test_purchase_channels_fixes_kind():
    assert PurchaseChannelsIn(name="Teste").kind == "purchase_channel"
    with pytest.raises(ValidationError):
        PurchaseChannelsIn(name="Teste", kind="supplier")
