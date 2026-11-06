"""Contrato específico de supplier."""

import pytest
from app.modules.auxiliaries.suppliers.schemas import SuppliersIn
from pydantic import ValidationError


def test_suppliers_fixes_kind():
    assert SuppliersIn(name="Teste").kind == "supplier"
    with pytest.raises(ValidationError):
        SuppliersIn(name="Teste", kind="category")
