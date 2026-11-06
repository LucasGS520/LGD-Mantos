"""Persistência do catálogo e dos acontecimentos versionados da operação."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.models.common import now, uid


class Control(Base):
    """Ponto único de serialização e início do histórico confiável."""

    __tablename__ = "lgd_control"
    __table_args__ = (CheckConstraint("id = 1"),)
    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    revision: Mapped[int] = mapped_column(default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Auxiliary(Base):
    """Cadastro simples; o tipo distingue fornecedor, categoria, canal e forma."""

    __tablename__ = "lgd_auxiliaries"
    __table_args__ = (UniqueConstraint("kind", "normalized_name"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    kind: Mapped[str] = mapped_column(String(30), index=True)
    name: Mapped[str] = mapped_column(String(255))
    normalized_name: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(default=True)
    version: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Product(Base):
    """Peça comercial reconhecida pela estampa, sem saldo editável."""

    __tablename__ = "lgd_products"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(255))
    print_name: Mapped[str] = mapped_column(String(255))
    brand: Mapped[str | None] = mapped_column(String(150))
    model: Mapped[str | None] = mapped_column(String(150))
    category_id: Mapped[str | None] = mapped_column(ForeignKey("lgd_auxiliaries.id"))
    notes: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(default=True)
    version: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Variant(Base):
    """Combinação vendável; o saldo e o custo médio são projeções do histórico."""

    __tablename__ = "lgd_variants"
    __table_args__ = (
        UniqueConstraint("product_id", "normalized_size", "normalized_color"),
        CheckConstraint("stock >= 0"),
        CheckConstraint("reference_cost IS NULL OR reference_cost >= 0"),
        CheckConstraint("reference_price IS NULL OR reference_price >= 0"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    product_id: Mapped[str] = mapped_column(ForeignKey("lgd_products.id"), index=True)
    code: Mapped[str] = mapped_column(String(40), unique=True)
    size: Mapped[str] = mapped_column(String(50))
    color: Mapped[str] = mapped_column(String(100))
    normalized_size: Mapped[str] = mapped_column(String(50))
    normalized_color: Mapped[str] = mapped_column(String(100))
    reference_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    reference_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    stock: Mapped[int] = mapped_column(default=0)
    average_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    active: Mapped[bool] = mapped_column(default=True)
    version: Mapped[int] = mapped_column(default=1)


class Photo(Base):
    """Arquivo validado pertencente ao produto, com ordem e destaque opcional."""

    __tablename__ = "lgd_photos"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    product_id: Mapped[str] = mapped_column(ForeignKey("lgd_products.id"), index=True)
    filename: Mapped[str] = mapped_column(String(100), unique=True)
    variant_id: Mapped[str | None] = mapped_column(ForeignKey("lgd_variants.id"))
    color: Mapped[str | None] = mapped_column(String(100))
    position: Mapped[int] = mapped_column(default=0)
    primary: Mapped[bool] = mapped_column(Boolean, default=False)


class Operation(Base):
    """Acontecimento com itens estruturados e projeção recalculável.

    Itens e pagamentos pertencem atomicamente ao documento JSON. Cada item
    identifica sua variante; pagamentos possuem identificadores estáveis. As
    versões anteriores são preservadas em Revision, nunca apagadas na edição.
    """

    __tablename__ = "lgd_operations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    sequence: Mapped[int] = mapped_column(Integer, unique=True)
    kind: Mapped[str] = mapped_column(String(20), index=True)
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    version: Mapped[int] = mapped_column(default=1)
    cancelled: Mapped[bool] = mapped_column(default=False)
    payload: Mapped[dict] = mapped_column(JSON)
    result: Mapped[dict] = mapped_column(JSON, default=dict)


class Movement(Base):
    """Efeito compensatório imutável ligado à versão da operação de origem."""

    __tablename__ = "lgd_movements"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    operation_id: Mapped[str] = mapped_column(ForeignKey("lgd_operations.id"), index=True)
    variant_id: Mapped[str] = mapped_column(ForeignKey("lgd_variants.id"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    delta: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Revision(Base):
    """Antes/depois de cada alteração confirmada pelo dono autenticado."""

    __tablename__ = "lgd_revisions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    entity_type: Mapped[str] = mapped_column(String(30))
    action: Mapped[str] = mapped_column(String(30))
    reason: Mapped[str] = mapped_column(Text)
    before: Mapped[dict | None] = mapped_column(JSON)
    after: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class RequestReceipt(Base):
    """Resultado de requisição para repetição segura, na mesma transação."""

    __tablename__ = "lgd_requests"
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64))
    response: Mapped[dict] = mapped_column(JSON)
