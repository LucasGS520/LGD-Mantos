import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Numeric, Boolean, Text, DateTime, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

def uid(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc)

class Category(Base):
    __tablename__ = "categories"
    id:   Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    products = relationship("Product", back_populates="category")

class Supplier(Base):
    __tablename__ = "suppliers"
    id:      Mapped[str]       = mapped_column(String(36), primary_key=True, default=uid)
    name:    Mapped[str]       = mapped_column(String(255), nullable=False)
    contact: Mapped[str|None]  = mapped_column(String(255), nullable=True)
    phone:   Mapped[str|None]  = mapped_column(String(50),  nullable=True)
    email:   Mapped[str|None]  = mapped_column(String(255), nullable=True)
    notes:   Mapped[str|None]  = mapped_column(Text, nullable=True)
    is_active: Mapped[bool]    = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    products = relationship("Product", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

class Product(Base):
    __tablename__ = "products"
    id:          Mapped[str]       = mapped_column(String(36), primary_key=True, default=uid)
    sku:         Mapped[str]       = mapped_column(String(50), unique=True, nullable=False)
    name:        Mapped[str]       = mapped_column(String(255), nullable=False)
    description: Mapped[str|None]  = mapped_column(Text, nullable=True)
    category_id: Mapped[str|None]  = mapped_column(String(36), ForeignKey("categories.id"), nullable=True)
    supplier_id: Mapped[str|None]  = mapped_column(String(36), ForeignKey("suppliers.id"), nullable=True)
    cost_price:  Mapped[float]     = mapped_column(Numeric(10,2), nullable=False, default=0)
    sale_price:  Mapped[float]     = mapped_column(Numeric(10,2), nullable=False, default=0)
    photos:      Mapped[list|None] = mapped_column(JSON, default=list)   # list of filenames
    notes:       Mapped[str|None]  = mapped_column(Text, nullable=True)
    is_active:   Mapped[bool]      = mapped_column(Boolean, default=True)
    created_at:  Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=now)
    updated_at:  Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    category = relationship("Category", back_populates="products")
    supplier  = relationship("Supplier",  back_populates="products")
    variants  = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")

class ProductVariant(Base):
    __tablename__ = "product_variants"
    id:              Mapped[str]       = mapped_column(String(36), primary_key=True, default=uid)
    product_id:      Mapped[str]       = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    size:            Mapped[str]       = mapped_column(String(20), nullable=False)
    color:           Mapped[str]       = mapped_column(String(50), nullable=False, default="Único")
    stock_quantity:  Mapped[int]       = mapped_column(Integer, default=0)
    min_stock_alert: Mapped[int]       = mapped_column(Integer, default=3)
    price_override:  Mapped[float|None]= mapped_column(Numeric(10,2), nullable=True)

    product = relationship("Product", back_populates="variants")
    stock_movements = relationship("StockMovement", back_populates="variant")
    sale_items      = relationship("SaleItem", back_populates="variant")

class StockMovement(Base):
    __tablename__ = "stock_movements"
    id:            Mapped[str]       = mapped_column(String(36), primary_key=True, default=uid)
    variant_id:    Mapped[str]       = mapped_column(String(36), ForeignKey("product_variants.id"), nullable=False)
    movement_type: Mapped[str]       = mapped_column(SAEnum("entrada","saida","ajuste","devolucao", name="mvt_type"), nullable=False)
    quantity:      Mapped[int]       = mapped_column(Integer, nullable=False)
    unit_cost:     Mapped[float|None]= mapped_column(Numeric(10,2), nullable=True)
    notes:         Mapped[str|None]  = mapped_column(Text, nullable=True)
    created_at:    Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=now)

    variant = relationship("ProductVariant", back_populates="stock_movements")

class Sale(Base):
    """Single-line sale record — no cart, no customer. Just: what sold, when, for how much, on which channel."""
    __tablename__ = "sales"
    id:         Mapped[str]       = mapped_column(String(36), primary_key=True, default=uid)
    sold_at:    Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=now)
    channel:    Mapped[str]       = mapped_column(String(50), default="loja")   # loja, instagram, whatsapp, site
    notes:      Mapped[str|None]  = mapped_column(Text, nullable=True)
    total:      Mapped[float]     = mapped_column(Numeric(10,2), nullable=False)
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

class SaleItem(Base):
    __tablename__ = "sale_items"
    id:         Mapped[str]  = mapped_column(String(36), primary_key=True, default=uid)
    sale_id:    Mapped[str]  = mapped_column(String(36), ForeignKey("sales.id"), nullable=False)
    variant_id: Mapped[str]  = mapped_column(String(36), ForeignKey("product_variants.id"), nullable=False)
    quantity:   Mapped[int]  = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float]= mapped_column(Numeric(10,2), nullable=False)
    unit_cost:  Mapped[float]= mapped_column(Numeric(10,2), nullable=False, default=0)

    sale    = relationship("Sale", back_populates="items")
    variant = relationship("ProductVariant", back_populates="sale_items")

class Expense(Base):
    __tablename__ = "expenses"
    id:          Mapped[str]       = mapped_column(String(36), primary_key=True, default=uid)
    date:        Mapped[str]       = mapped_column(String(10), nullable=False)   # YYYY-MM-DD
    category:    Mapped[str]       = mapped_column(String(100), nullable=False)
    amount:      Mapped[float]     = mapped_column(Numeric(10,2), nullable=False)
    description: Mapped[str|None]  = mapped_column(Text, nullable=True)
    supplier_id: Mapped[str|None]  = mapped_column(String(36), ForeignKey("suppliers.id"), nullable=True)
    created_at:  Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=now)

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id:          Mapped[str]       = mapped_column(String(36), primary_key=True, default=uid)
    supplier_id: Mapped[str]       = mapped_column(String(36), ForeignKey("suppliers.id"), nullable=False)
    order_date:  Mapped[str]       = mapped_column(String(10), nullable=False)   # YYYY-MM-DD
    status:      Mapped[str]       = mapped_column(SAEnum("rascunho","enviado","recebido","cancelado", name="po_status"), default="rascunho")
    notes:       Mapped[str|None]  = mapped_column(Text, nullable=True)
    created_at:  Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=now)

    supplier = relationship("Supplier", back_populates="purchase_orders")
    items    = relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan")

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    id:         Mapped[str]  = mapped_column(String(36), primary_key=True, default=uid)
    order_id:   Mapped[str]  = mapped_column(String(36), ForeignKey("purchase_orders.id"), nullable=False)
    variant_id: Mapped[str]  = mapped_column(String(36), ForeignKey("product_variants.id"), nullable=False)
    quantity:   Mapped[int]  = mapped_column(Integer, nullable=False)
    unit_cost:  Mapped[float]= mapped_column(Numeric(10,2), nullable=False)
    order   = relationship("PurchaseOrder", back_populates="items")
