"""As regras arquiteturais devem detectar imports diretos e efeitos nas rotas."""

import check_boundaries


def test_domain_rejects_direct_infrastructure_import(tmp_path, monkeypatch):
    folder = tmp_path / "modules" / "example" / "domain"
    folder.mkdir(parents=True)
    (folder / "rule.py").write_text(
        "import sqlalchemy\nfrom fastapi import HTTPException\n", encoding="utf-8"
    )
    monkeypatch.setattr(check_boundaries, "ROOT", tmp_path)
    errors = check_boundaries.violations()
    assert any("sqlalchemy" in error for error in errors)
    assert any("fastapi" in error for error in errors)


def test_router_rejects_transaction_control(tmp_path, monkeypatch):
    (tmp_path / "router.py").write_text(
        "async def write(db):\n    await db.commit()\n", encoding="utf-8"
    )
    monkeypatch.setattr(check_boundaries, "ROOT", tmp_path)
    assert any("infraestrutura na borda HTTP" in error for error in check_boundaries.violations())


def test_pure_calculation_is_allowed(tmp_path, monkeypatch):
    folder = tmp_path / "modules" / "example" / "domain"
    folder.mkdir(parents=True)
    (folder / "rule.py").write_text(
        "from decimal import Decimal\ndef total(value):\n    return Decimal(value)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(check_boundaries, "ROOT", tmp_path)
    assert check_boundaries.violations() == []
