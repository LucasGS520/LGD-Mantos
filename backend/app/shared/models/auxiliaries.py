"""Cadastros distintos permitem referências tipadas por foreign keys reais."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from .common import now, uid
from .metadata import Base


class AuxiliaryFields:
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(255))
    normalized_name: Mapped[str] = mapped_column(String(255), unique=True)
    notes: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(default=True, server_default=text("true"))
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now, server_default=text("now()")
    )

    @declared_attr.directive
    def __table_args__(cls):
        return (
            CheckConstraint("version > 0", name="version_positive"),
            CheckConstraint(
                "btrim(name) <> '' AND btrim(normalized_name) <> ''", name="names_nonempty"
            ),
        )


class Supplier(AuxiliaryFields, Base):
    __tablename__ = "lgd_suppliers"
    kind = "supplier"


class Category(AuxiliaryFields, Base):
    __tablename__ = "lgd_categories"
    kind = "category"


class PurchaseChannel(AuxiliaryFields, Base):
    __tablename__ = "lgd_purchase_channels"
    kind = "purchase_channel"


class SaleChannel(AuxiliaryFields, Base):
    __tablename__ = "lgd_sale_channels"
    kind = "sale_channel"


class PaymentMethod(AuxiliaryFields, Base):
    __tablename__ = "lgd_payment_methods"
    kind = "payment_method"


AUXILIARY_MODELS = {
    model.kind: model for model in (Supplier, Category, PurchaseChannel, SaleChannel, PaymentMethod)
}
