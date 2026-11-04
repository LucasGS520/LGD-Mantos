"""Cria o núcleo alinhado sem apagar dados legados durante o desenvolvimento.

A limpeza legada é administrativa e explícita, fora do startup. Este esquema
é descrito integralmente aqui para manter a migration independente do ORM.
"""

from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("lgd_control", sa.Column("id", sa.Integer, primary_key=True), sa.Column("revision", sa.Integer, nullable=False), sa.Column("started_at", sa.DateTime(timezone=True)), sa.CheckConstraint("id = 1"))
    op.create_table("lgd_auxiliaries", sa.Column("id", sa.String(36), primary_key=True), sa.Column("kind", sa.String(30), nullable=False), sa.Column("name", sa.String(255), nullable=False), sa.Column("normalized_name", sa.String(255), nullable=False), sa.Column("notes", sa.Text), sa.Column("active", sa.Boolean, nullable=False), sa.Column("version", sa.Integer, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("kind", "normalized_name"))
    op.create_table("lgd_products", sa.Column("id", sa.String(36), primary_key=True), sa.Column("name", sa.String(255), nullable=False), sa.Column("print_name", sa.String(255), nullable=False), sa.Column("brand", sa.String(150)), sa.Column("model", sa.String(150)), sa.Column("category_id", sa.String(36), sa.ForeignKey("lgd_auxiliaries.id")), sa.Column("notes", sa.Text), sa.Column("active", sa.Boolean, nullable=False), sa.Column("version", sa.Integer, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("lgd_variants", sa.Column("id", sa.String(36), primary_key=True), sa.Column("product_id", sa.String(36), sa.ForeignKey("lgd_products.id"), nullable=False), sa.Column("code", sa.String(40), nullable=False, unique=True), sa.Column("size", sa.String(50), nullable=False), sa.Column("color", sa.String(100), nullable=False), sa.Column("normalized_size", sa.String(50), nullable=False), sa.Column("normalized_color", sa.String(100), nullable=False), sa.Column("reference_cost", sa.Numeric(14, 2)), sa.Column("reference_price", sa.Numeric(14, 2)), sa.Column("stock", sa.Integer, nullable=False), sa.Column("average_cost", sa.Numeric(14, 2)), sa.Column("active", sa.Boolean, nullable=False), sa.Column("version", sa.Integer, nullable=False), sa.UniqueConstraint("product_id", "normalized_size", "normalized_color"), sa.CheckConstraint("stock >= 0"), sa.CheckConstraint("reference_cost IS NULL OR reference_cost >= 0"), sa.CheckConstraint("reference_price IS NULL OR reference_price >= 0"))
    op.create_table("lgd_photos", sa.Column("id", sa.String(36), primary_key=True), sa.Column("product_id", sa.String(36), sa.ForeignKey("lgd_products.id"), nullable=False), sa.Column("filename", sa.String(100), nullable=False, unique=True), sa.Column("variant_id", sa.String(36), sa.ForeignKey("lgd_variants.id")), sa.Column("color", sa.String(100)), sa.Column("position", sa.Integer, nullable=False), sa.Column("primary", sa.Boolean, nullable=False))
    op.create_table("lgd_operations", sa.Column("id", sa.String(36), primary_key=True), sa.Column("sequence", sa.Integer, nullable=False, unique=True), sa.Column("kind", sa.String(20), nullable=False), sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.Column("version", sa.Integer, nullable=False), sa.Column("cancelled", sa.Boolean, nullable=False), sa.Column("payload", sa.JSON, nullable=False), sa.Column("result", sa.JSON, nullable=False))
    op.create_table("lgd_movements", sa.Column("id", sa.String(36), primary_key=True), sa.Column("operation_id", sa.String(36), sa.ForeignKey("lgd_operations.id"), nullable=False), sa.Column("variant_id", sa.String(36), sa.ForeignKey("lgd_variants.id"), nullable=False), sa.Column("version", sa.Integer, nullable=False), sa.Column("delta", sa.Integer, nullable=False), sa.Column("reason", sa.Text, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("lgd_revisions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("entity_id", sa.String(36), nullable=False), sa.Column("entity_type", sa.String(30), nullable=False), sa.Column("action", sa.String(30), nullable=False), sa.Column("reason", sa.Text, nullable=False), sa.Column("before", sa.JSON), sa.Column("after", sa.JSON), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("lgd_requests", sa.Column("key", sa.String(100), primary_key=True), sa.Column("fingerprint", sa.String(64), nullable=False), sa.Column("response", sa.JSON, nullable=False))
    for table, columns in {"lgd_auxiliaries": ["kind"], "lgd_variants": ["product_id"], "lgd_photos": ["product_id"], "lgd_operations": ["kind", "effective_at"], "lgd_movements": ["operation_id", "variant_id"], "lgd_revisions": ["entity_id"]}.items():
        for column in columns:
            op.create_index(f"ix_{table}_{column}", table, [column])


def downgrade():
    for table in ("lgd_requests", "lgd_revisions", "lgd_movements", "lgd_operations", "lgd_photos", "lgd_variants", "lgd_products", "lgd_auxiliaries", "lgd_control"):
        op.drop_table(table)
