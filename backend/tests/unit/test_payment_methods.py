"""Contrato específico de payment_method."""

import pytest
from app.modules.auxiliaries.payment_methods.schemas import PaymentMethodsIn
from pydantic import ValidationError


def test_payment_methods_fixes_kind():
    assert PaymentMethodsIn(name="Teste").kind == "payment_method"
    with pytest.raises(ValidationError):
        PaymentMethodsIn(name="Teste", kind="supplier")
