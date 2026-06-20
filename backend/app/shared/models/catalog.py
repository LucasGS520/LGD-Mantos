"""Modelos ORM do catálogo de produtos, fornecedores e variantes."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.models.common import now, uid


class Category(Base):
    """Categoria comercial usada para organizar produtos do catálogo."""

    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    products = relationship("Product", back_populates="category")


class Supplier(Base):
    """Fornecedor de produtos e compras da loja."""

    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    products = relationship("Product", back_populates="supplier")
    merchandise_entries = relationship("MerchandiseEntry", back_populates="supplier")


class SaleChannel(Base):
    """Canal de venda pelo qual as transações podem ser realizadas."""

    __tablename__ = "sale_channels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(20), nullable=False, default="#D4A847")
    fee_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    monthly_goal: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    sales = relationship("Sale", back_populates="sale_channel")


class Product(Base):
    """Produto principal vendido pela loja, identificado por SKU único."""

    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("categories.id"), nullable=True)
    supplier_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("suppliers.id"), nullable=True)
    cost_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    sale_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    photos: Mapped[list | None] = mapped_column(JSON, default=list)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    product_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, default=list)

    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")


class ProductVariant(Base):
    """Variação vendável de um produto, com estoque próprio por tamanho/cor."""

    __tablename__ = "product_variants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    size: Mapped[str] = mapped_column(String(20), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False, default="Unico")
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    price_override: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    product = relationship("Product", back_populates="variants")
    stock_movements = relationship("StockMovement", back_populates="variant")
    sale_items = relationship("SaleItem", back_populates="variant")
