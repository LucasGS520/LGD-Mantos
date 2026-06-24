"""Modelos ORM das operações de estoque, venda, despesa e entrada de mercadoria."""

from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.models.common import now, uid


class StockMovement(Base):
    """Registro histórico de entrada ou saída de estoque."""

    __tablename__ = "stock_movements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    variant_id: Mapped[str] = mapped_column(String(36), ForeignKey("product_variants.id"), nullable=False)
    movement_type: Mapped[str] = mapped_column(
        SAEnum("entrada", "saida", name="mvt_type"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    variant = relationship("ProductVariant", back_populates="stock_movements")


class Sale(Base):
    """Venda realizada em um canal, composta por um ou mais itens."""

    __tablename__ = "sales"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    sold_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    sale_channel_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("sale_channels.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    sale_channel = relationship("SaleChannel", back_populates="sales")


class SaleItem(Base):
    """Item individual de uma venda, vinculado a uma variante de produto."""

    __tablename__ = "sale_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    sale_id: Mapped[str] = mapped_column(String(36), ForeignKey("sales.id"), nullable=False)
    variant_id: Mapped[str] = mapped_column(String(36), ForeignKey("product_variants.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    sale = relationship("Sale", back_populates="items")
    variant = relationship("ProductVariant", back_populates="sale_items")


class Expense(Base):
    """Despesa financeira usada nos cálculos de resultado da loja."""

    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    date: Mapped[str] = mapped_column(String(10), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    supplier_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("suppliers.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class MerchandiseEntry(Base):
    """Registro de entrada de mercadoria recebida de um fornecedor."""

    __tablename__ = "merchandise_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    supplier_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("suppliers.id"), nullable=True)
    entry_date: Mapped[str] = mapped_column(String(10), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    supplier = relationship("Supplier", back_populates="merchandise_entries")
    items = relationship("MerchandiseEntryItem", back_populates="entry", cascade="all, delete-orphan")


class MerchandiseEntryItem(Base):
    """Item de uma entrada de mercadoria, vinculado a uma variante de produto."""

    __tablename__ = "merchandise_entry_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    entry_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchandise_entries.id"), nullable=False)
    variant_id: Mapped[str] = mapped_column(String(36), ForeignKey("product_variants.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    entry = relationship("MerchandiseEntry", back_populates="items")
    variant = relationship("ProductVariant")
