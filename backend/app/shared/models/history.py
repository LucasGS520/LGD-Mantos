"""Rastreabilidade durável, sem retenção automática de histórico ou recibos."""

from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .common import now, uid
from .metadata import Base


class Control(Base):
    __tablename__ = "lgd_control"
    __table_args__ = (CheckConstraint("id = 1 AND revision >= 0", name="singleton_revision"),)
    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    revision: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Movement(Base):
    __tablename__ = "lgd_movements"
    __table_args__ = (
        CheckConstraint("version > 0 AND delta <> 0", name="version_delta"),
        CheckConstraint("btrim(reason) <> ''", name="reason_nonempty"),
        Index("ix_lgd_movements_origin", "operation_id", "created_at", "id"),
    )
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=uid)
    operation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("lgd_operations.id", ondelete="RESTRICT")
    )
    variant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("lgd_variants.id", ondelete="RESTRICT"), index=True
    )
    version: Mapped[int] = mapped_column()
    delta: Mapped[int] = mapped_column()
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now, server_default=text("now()")
    )


class Revision(Base):
    __tablename__ = "lgd_revisions"
    __table_args__ = (
        Index("ix_lgd_revisions_origin", "entity_id", "created_at", "id"),
        CheckConstraint(
            "entity_type IN ('auxiliary','product','variant','photo','operation') AND action IN ('create','edit','remove','replace','cancel','recalculate')",
            name="types_valid",
        ),
        CheckConstraint("document_version > 0 AND btrim(reason) <> ''", name="version_reason"),
        CheckConstraint(
            '("before" IS NULL OR jsonb_typeof("before") = \'object\') AND ("after" IS NULL OR jsonb_typeof("after") = \'object\') AND ("before" IS NOT NULL OR "after" IS NOT NULL)',
            name="snapshots_objects",
        ),
    )
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=uid)
    entity_id: Mapped[str] = mapped_column(UUID(as_uuid=False))
    entity_type: Mapped[str] = mapped_column(String(30))
    action: Mapped[str] = mapped_column(String(30))
    reason: Mapped[str] = mapped_column(Text)
    before: Mapped[dict | None] = mapped_column(JSONB(none_as_null=True))
    after: Mapped[dict | None] = mapped_column(JSONB(none_as_null=True))
    document_version: Mapped[int] = mapped_column(default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now, server_default=text("now()")
    )


class RequestReceipt(Base):
    __tablename__ = "lgd_requests"
    __table_args__ = (
        CheckConstraint(
            "length(key) > 0 AND fingerprint ~ '^[0-9a-f]{64}$'", name="key_fingerprint"
        ),
        CheckConstraint(
            "document_version > 0 AND jsonb_typeof(response) = 'object'", name="document_valid"
        ),
    )
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    operation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("lgd_operations.id", ondelete="RESTRICT")
    )
    fingerprint: Mapped[str] = mapped_column(String(64))
    response: Mapped[dict] = mapped_column(JSONB)
    document_version: Mapped[int] = mapped_column(default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now, server_default=text("now()")
    )
