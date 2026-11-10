"""Identidade comercial e vínculo consistente entre produto, variante e foto."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .common import now, uid
from .metadata import Base


class Product(Base):
    __tablename__ = "lgd_products"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        CheckConstraint("btrim(name) <> '' AND btrim(print_name) <> ''", name="names_nonempty"),
    )
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(255))
    print_name: Mapped[str] = mapped_column(String(255))
    brand: Mapped[str | None] = mapped_column(String(150))
    model: Mapped[str | None] = mapped_column(String(150))
    category_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("lgd_categories.id", ondelete="RESTRICT")
    )
    notes: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(default=True, server_default=text("true"))
    version: Mapped[int] = mapped_column(default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now, server_default=text("now()")
    )


class Variant(Base):
    __tablename__ = "lgd_variants"
    __table_args__ = (
        UniqueConstraint("product_id", "normalized_size", "normalized_color"),
        UniqueConstraint("product_id", "id", name="uq_lgd_variants_product_id_id"),
        CheckConstraint("stock >= 0 AND version > 0", name="stock_version"),
        CheckConstraint(
            "btrim(size) <> '' AND btrim(color) <> '' AND btrim(normalized_size) <> '' AND btrim(normalized_color) <> ''",
            name="identity_nonempty",
        ),
        *(
            CheckConstraint(
                f"{field} IS NULL OR ({field} >= 0 AND {field} <> 'NaN'::numeric)",
                name=field + "_valid",
            )
            for field in ("reference_cost", "reference_price", "average_cost")
        ),
    )
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=uid)
    product_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("lgd_products.id", ondelete="RESTRICT")
    )
    code: Mapped[str] = mapped_column(String(40), unique=True)
    size: Mapped[str] = mapped_column(String(50))
    color: Mapped[str] = mapped_column(String(100))
    normalized_size: Mapped[str] = mapped_column(String(50))
    normalized_color: Mapped[str] = mapped_column(String(100))
    reference_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    reference_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    stock: Mapped[int] = mapped_column(default=0, server_default="0")
    average_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    active: Mapped[bool] = mapped_column(default=True, server_default=text("true"))
    version: Mapped[int] = mapped_column(default=1, server_default="1")


class Photo(Base):
    __tablename__ = "lgd_photos"
    __table_args__ = (
        ForeignKeyConstraint(
            ["product_id", "variant_id"],
            ["lgd_variants.product_id", "lgd_variants.id"],
            ondelete="RESTRICT",
        ),
        CheckConstraint("position >= 0", name="position_nonnegative"),
        Index(
            "uq_lgd_photos_primary", "product_id", unique=True, postgresql_where=text('"primary"')
        ),
        Index("ix_lgd_photos_product_order", "product_id", "position", "id"),
    )
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=uid)
    product_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("lgd_products.id", ondelete="RESTRICT")
    )
    filename: Mapped[str] = mapped_column(String(100), unique=True)
    variant_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    color: Mapped[str | None] = mapped_column(String(100))
    position: Mapped[int] = mapped_column(default=0, server_default="0")
    primary: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
