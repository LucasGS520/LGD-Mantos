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


def test_cross_module_private_import_rejected_and_public_allowed(tmp_path, monkeypatch):
    for module in ("catalog", "operations"):
        folder = tmp_path / "modules" / module
        folder.mkdir(parents=True)
        (folder / "public.py").write_text("", encoding="utf-8")
        (folder / "repository.py").write_text("", encoding="utf-8")
    source = tmp_path / "modules" / "operations" / "service.py"
    monkeypatch.setattr(check_boundaries, "ROOT", tmp_path)
    source.write_text("from app.modules.catalog.repository import products\n", encoding="utf-8")
    assert any("não permitida" in error for error in check_boundaries.violations())
    source.write_text("from app.modules.catalog.public import products\n", encoding="utf-8")
    assert check_boundaries.violations() == []


def test_relative_cycle_is_detected(tmp_path, monkeypatch):
    (tmp_path / "a.py").write_text("from . import b\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("from . import a\n", encoding="utf-8")
    monkeypatch.setattr(check_boundaries, "ROOT", tmp_path)
    assert any("Ciclo:" in error for error in check_boundaries.violations())


def test_package_can_import_sibling_without_self_cycle(tmp_path, monkeypatch):
    folder = tmp_path / "rules"
    folder.mkdir()
    (folder / "__init__.py").write_text("from . import one\n", encoding="utf-8")
    (folder / "one.py").write_text("", encoding="utf-8")
    monkeypatch.setattr(check_boundaries, "ROOT", tmp_path)
    assert check_boundaries.violations() == []
