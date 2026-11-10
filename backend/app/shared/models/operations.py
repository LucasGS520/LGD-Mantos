"""Agregado relacional: filhos pertencem à mesma confirmação transacional."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
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
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .common import now, uid
from .metadata import Base


class Operation(Base):
    __tablename__ = "lgd_operations"
    __table_args__ = (
        UniqueConstraint("id", "kind", name="uq_lgd_operations_id_kind"),
        CheckConstraint("kind IN ('inventory','purchase','sale','adjustment')", name="kind_valid"),
        CheckConstraint(
            "sequence > 0 AND version > 0 AND document_version > 0", name="versions_positive"
        ),
        CheckConstraint("kind <> 'inventory' OR NOT cancelled", name="inventory_not_cancelled"),
        CheckConstraint(
            "(kind = 'purchase' AND supplier_id IS NOT NULL AND purchase_channel_id IS NOT NULL AND purchase_date IS NOT NULL AND sale_channel_id IS NULL AND direction IS NULL) OR (kind = 'sale' AND sale_channel_id IS NOT NULL AND supplier_id IS NULL AND purchase_channel_id IS NULL AND purchase_date IS NULL AND direction IS NULL) OR (kind = 'inventory' AND supplier_id IS NULL AND purchase_channel_id IS NULL AND sale_channel_id IS NULL AND purchase_date IS NULL AND direction IS NULL) OR (kind = 'adjustment' AND supplier_id IS NULL AND purchase_channel_id IS NULL AND sale_channel_id IS NULL AND purchase_date IS NULL AND direction IS NOT NULL AND direction IN ('in','out') AND reason IS NOT NULL AND btrim(reason) <> '')",
            name="fields_match_kind",
        ),
        CheckConstraint(
            "jsonb_typeof(labels) = 'object' AND jsonb_typeof(result) = 'object'",
            name="documents_objects",
        ),
        Index(
            "uq_lgd_operations_inventory",
            "kind",
            unique=True,
            postgresql_where=text("kind = 'inventory'"),
        ),
    )
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=uid)
    sequence: Mapped[int] = mapped_column(BigInteger, unique=True)
    kind: Mapped[str] = mapped_column(String(20))
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now, server_default=text("now()")
    )
    version: Mapped[int] = mapped_column(default=1, server_default="1")
    cancelled: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
    document_version: Mapped[int] = mapped_column(default=1, server_default="1")
    purchase_date: Mapped[date | None] = mapped_column(Date)
    supplier_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("lgd_suppliers.id", ondelete="RESTRICT")
    )
    purchase_channel_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("lgd_purchase_channels.id", ondelete="RESTRICT")
    )
    sale_channel_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("lgd_sale_channels.id", ondelete="RESTRICT")
    )
    direction: Mapped[str | None] = mapped_column(String(3))
    reason: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    labels: Mapped[dict] = mapped_column(JSONB, default=dict, server_default=text("'{}'::jsonb"))
    result: Mapped[dict] = mapped_column(JSONB, default=dict, server_default=text("'{}'::jsonb"))


class OperationItem(Base):
    __tablename__ = "lgd_operation_items"
    __table_args__ = (
        ForeignKeyConstraint(
            ["operation_id", "operation_kind"],
            ["lgd_operations.id", "lgd_operations.kind"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("operation_id", "variant_id"),
        CheckConstraint("position >= 0 AND quantity > 0", name="quantity_position"),
        CheckConstraint(
            "unit_cost IS NULL OR (unit_cost >= 0 AND unit_cost <> 'NaN'::numeric)",
            name="cost_valid",
        ),
        CheckConstraint(
            "(operation_kind = 'sale' AND unit_price IS NOT NULL AND unit_price > 0 AND unit_price <> 'NaN'::numeric AND unit_cost IS NULL) OR (operation_kind = 'purchase' AND unit_price IS NULL AND unit_cost IS NOT NULL AND unit_cost > 0) OR (operation_kind IN ('inventory','adjustment') AND unit_price IS NULL)",
            name="values_match_kind",
        ),
        CheckConstraint("jsonb_typeof(snapshot) = 'object'", name="snapshot_object"),
    )
    operation_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    position: Mapped[int] = mapped_column(primary_key=True)
    operation_kind: Mapped[str] = mapped_column(String(20))
    variant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("lgd_variants.id", ondelete="RESTRICT")
    )
    quantity: Mapped[int] = mapped_column()
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    snapshot: Mapped[dict] = mapped_column(JSONB)


class SalePayment(Base):
    __tablename__ = "lgd_sale_payments"
    __table_args__ = (
        UniqueConstraint(
            "operation_id",
            "position",
            name="uq_lgd_sale_payments_position",
            deferrable=True,
            initially="DEFERRED",
        ),
        ForeignKeyConstraint(
            ["operation_id", "operation_kind"],
            ["lgd_operations.id", "lgd_operations.kind"],
            ondelete="RESTRICT",
        ),
        CheckConstraint("operation_kind = 'sale'", name="sale_only"),
        CheckConstraint(
            "amount > 0 AND amount <> 'NaN'::numeric AND position >= 0", name="amount_position"
        ),
    )
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=uid)
    operation_id: Mapped[str] = mapped_column(UUID(as_uuid=False))
    operation_kind: Mapped[str] = mapped_column(String(20), default="sale", server_default="sale")
    position: Mapped[int] = mapped_column()
    method_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("lgd_payment_methods.id", ondelete="RESTRICT")
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    method_name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now, server_default=text("now()")
    )
