"""Contrato específico de category."""

import pytest
from app.modules.auxiliaries.categories.schemas import CategoriesIn
from pydantic import ValidationError


def test_categories_fixes_kind():
    assert CategoriesIn(name="Teste").kind == "category"
    with pytest.raises(ValidationError):
        CategoriesIn(name="Teste", kind="supplier")
