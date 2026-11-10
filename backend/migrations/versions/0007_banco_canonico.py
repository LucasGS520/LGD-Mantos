"""Baseline canônica imutável: relacional, UUID e histórico JSONB.

DDL congelada nesta revisão; não importa modelos ou configuração da API.
"""

from alembic import op
from sqlalchemy import inspect

revision = "0007"
down_revision = None
branch_labels = None
depends_on = None

DDL = [
    """CREATE TABLE lgd_suppliers (
	id UUID NOT NULL,
	name VARCHAR(255) NOT NULL,
	normalized_name VARCHAR(255) NOT NULL,
	notes TEXT,
	active BOOLEAN DEFAULT true NOT NULL,
	version INTEGER DEFAULT '1' NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_lgd_suppliers PRIMARY KEY (id),
	CONSTRAINT ck_lgd_suppliers_version_positive CHECK (version > 0),
	CONSTRAINT ck_lgd_suppliers_names_nonempty CHECK (btrim(name) <> '' AND btrim(normalized_name) <> ''),
	CONSTRAINT uq_lgd_suppliers_normalized_name UNIQUE (normalized_name)
)""",
    """CREATE TABLE lgd_categories (
	id UUID NOT NULL,
	name VARCHAR(255) NOT NULL,
	normalized_name VARCHAR(255) NOT NULL,
	notes TEXT,
	active BOOLEAN DEFAULT true NOT NULL,
	version INTEGER DEFAULT '1' NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_lgd_categories PRIMARY KEY (id),
	CONSTRAINT ck_lgd_categories_version_positive CHECK (version > 0),
	CONSTRAINT ck_lgd_categories_names_nonempty CHECK (btrim(name) <> '' AND btrim(normalized_name) <> ''),
	CONSTRAINT uq_lgd_categories_normalized_name UNIQUE (normalized_name)
)""",
    """CREATE TABLE lgd_purchase_channels (
	id UUID NOT NULL,
	name VARCHAR(255) NOT NULL,
	normalized_name VARCHAR(255) NOT NULL,
	notes TEXT,
	active BOOLEAN DEFAULT true NOT NULL,
	version INTEGER DEFAULT '1' NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_lgd_purchase_channels PRIMARY KEY (id),
	CONSTRAINT ck_lgd_purchase_channels_version_positive CHECK (version > 0),
	CONSTRAINT ck_lgd_purchase_channels_names_nonempty CHECK (btrim(name) <> '' AND btrim(normalized_name) <> ''),
	CONSTRAINT uq_lgd_purchase_channels_normalized_name UNIQUE (normalized_name)
)""",
    """CREATE TABLE lgd_sale_channels (
	id UUID NOT NULL,
	name VARCHAR(255) NOT NULL,
	normalized_name VARCHAR(255) NOT NULL,
	notes TEXT,
	active BOOLEAN DEFAULT true NOT NULL,
	version INTEGER DEFAULT '1' NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_lgd_sale_channels PRIMARY KEY (id),
	CONSTRAINT ck_lgd_sale_channels_version_positive CHECK (version > 0),
	CONSTRAINT ck_lgd_sale_channels_names_nonempty CHECK (btrim(name) <> '' AND btrim(normalized_name) <> ''),
	CONSTRAINT uq_lgd_sale_channels_normalized_name UNIQUE (normalized_name)
)""",
    """CREATE TABLE lgd_payment_methods (
	id UUID NOT NULL,
	name VARCHAR(255) NOT NULL,
	normalized_name VARCHAR(255) NOT NULL,
	notes TEXT,
	active BOOLEAN DEFAULT true NOT NULL,
	version INTEGER DEFAULT '1' NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_lgd_payment_methods PRIMARY KEY (id),
	CONSTRAINT ck_lgd_payment_methods_version_positive CHECK (version > 0),
	CONSTRAINT ck_lgd_payment_methods_names_nonempty CHECK (btrim(name) <> '' AND btrim(normalized_name) <> ''),
	CONSTRAINT uq_lgd_payment_methods_normalized_name UNIQUE (normalized_name)
)""",
    """CREATE TABLE lgd_control (
	id INTEGER NOT NULL,
	revision BIGINT DEFAULT '0' NOT NULL,
	started_at TIMESTAMP WITH TIME ZONE,
	CONSTRAINT pk_lgd_control PRIMARY KEY (id),
	CONSTRAINT ck_lgd_control_singleton_revision CHECK (id = 1 AND revision >= 0)
)""",
    """CREATE TABLE lgd_revisions (
	id UUID NOT NULL,
	entity_id UUID NOT NULL,
	entity_type VARCHAR(30) NOT NULL,
	action VARCHAR(30) NOT NULL,
	reason TEXT NOT NULL,
	before JSONB,
	after JSONB,
	document_version INTEGER DEFAULT '1' NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_lgd_revisions PRIMARY KEY (id),
	CONSTRAINT ck_lgd_revisions_types_valid CHECK (entity_type IN ('auxiliary','product','variant','photo','operation') AND action IN ('create','edit','remove','replace','cancel','recalculate')),
	CONSTRAINT ck_lgd_revisions_version_reason CHECK (document_version > 0 AND btrim(reason) <> ''),
	CONSTRAINT ck_lgd_revisions_snapshots_objects CHECK ((\"before\" IS NULL OR jsonb_typeof(\"before\") = 'object') AND (\"after\" IS NULL OR jsonb_typeof(\"after\") = 'object') AND (\"before\" IS NOT NULL OR \"after\" IS NOT NULL))
)""",
    """CREATE INDEX ix_lgd_revisions_origin ON lgd_revisions (entity_id, created_at, id)""",
    """CREATE TABLE lgd_products (
	id UUID NOT NULL,
	name VARCHAR(255) NOT NULL,
	print_name VARCHAR(255) NOT NULL,
	brand VARCHAR(150),
	model VARCHAR(150),
	category_id UUID,
	notes TEXT,
	active BOOLEAN DEFAULT true NOT NULL,
	version INTEGER DEFAULT '1' NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_lgd_products PRIMARY KEY (id),
	CONSTRAINT ck_lgd_products_version_positive CHECK (version > 0),
	CONSTRAINT ck_lgd_products_names_nonempty CHECK (btrim(name) <> '' AND btrim(print_name) <> ''),
	CONSTRAINT fk_lgd_products_category_id_lgd_categories FOREIGN KEY(category_id) REFERENCES lgd_categories (id) ON DELETE RESTRICT
)""",
    """CREATE TABLE lgd_operations (
	id UUID NOT NULL,
	sequence BIGINT NOT NULL,
	kind VARCHAR(20) NOT NULL,
	effective_at TIMESTAMP WITH TIME ZONE NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	version INTEGER DEFAULT '1' NOT NULL,
	cancelled BOOLEAN DEFAULT false NOT NULL,
	document_version INTEGER DEFAULT '1' NOT NULL,
	purchase_date DATE,
	supplier_id UUID,
	purchase_channel_id UUID,
	sale_channel_id UUID,
	direction VARCHAR(3),
	reason TEXT,
	notes TEXT,
	labels JSONB DEFAULT '{}'::jsonb NOT NULL,
	result JSONB DEFAULT '{}'::jsonb NOT NULL,
	CONSTRAINT pk_lgd_operations PRIMARY KEY (id),
	CONSTRAINT uq_lgd_operations_id_kind UNIQUE (id, kind),
	CONSTRAINT ck_lgd_operations_kind_valid CHECK (kind IN ('inventory','purchase','sale','adjustment')),
	CONSTRAINT ck_lgd_operations_versions_positive CHECK (sequence > 0 AND version > 0 AND document_version > 0),
	CONSTRAINT ck_lgd_operations_inventory_not_cancelled CHECK (kind <> 'inventory' OR NOT cancelled),
	CONSTRAINT ck_lgd_operations_fields_match_kind CHECK ((kind = 'purchase' AND supplier_id IS NOT NULL AND purchase_channel_id IS NOT NULL AND purchase_date IS NOT NULL AND sale_channel_id IS NULL AND direction IS NULL) OR (kind = 'sale' AND sale_channel_id IS NOT NULL AND supplier_id IS NULL AND purchase_channel_id IS NULL AND purchase_date IS NULL AND direction IS NULL) OR (kind = 'inventory' AND supplier_id IS NULL AND purchase_channel_id IS NULL AND sale_channel_id IS NULL AND purchase_date IS NULL AND direction IS NULL) OR (kind = 'adjustment' AND supplier_id IS NULL AND purchase_channel_id IS NULL AND sale_channel_id IS NULL AND purchase_date IS NULL AND direction IS NOT NULL AND direction IN ('in','out') AND reason IS NOT NULL AND btrim(reason) <> '')),
	CONSTRAINT ck_lgd_operations_documents_objects CHECK (jsonb_typeof(labels) = 'object' AND jsonb_typeof(result) = 'object'),
	CONSTRAINT uq_lgd_operations_sequence UNIQUE (sequence),
	CONSTRAINT fk_lgd_operations_supplier_id_lgd_suppliers FOREIGN KEY(supplier_id) REFERENCES lgd_suppliers (id) ON DELETE RESTRICT,
	CONSTRAINT fk_lgd_operations_purchase_channel_id_lgd_purchase_channels FOREIGN KEY(purchase_channel_id) REFERENCES lgd_purchase_channels (id) ON DELETE RESTRICT,
	CONSTRAINT fk_lgd_operations_sale_channel_id_lgd_sale_channels FOREIGN KEY(sale_channel_id) REFERENCES lgd_sale_channels (id) ON DELETE RESTRICT
)""",
    """CREATE UNIQUE INDEX uq_lgd_operations_inventory ON lgd_operations (kind) WHERE kind = 'inventory'""",
    """CREATE TABLE lgd_variants (
	id UUID NOT NULL,
	product_id UUID NOT NULL,
	code VARCHAR(40) NOT NULL,
	size VARCHAR(50) NOT NULL,
	color VARCHAR(100) NOT NULL,
	normalized_size VARCHAR(50) NOT NULL,
	normalized_color VARCHAR(100) NOT NULL,
	reference_cost NUMERIC(14, 2),
	reference_price NUMERIC(14, 2),
	stock INTEGER DEFAULT '0' NOT NULL,
	average_cost NUMERIC(14, 2),
	active BOOLEAN DEFAULT true NOT NULL,
	version INTEGER DEFAULT '1' NOT NULL,
	CONSTRAINT pk_lgd_variants PRIMARY KEY (id),
	CONSTRAINT uq_lgd_variants_product_id UNIQUE (product_id, normalized_size, normalized_color),
	CONSTRAINT uq_lgd_variants_product_id_id UNIQUE (product_id, id),
	CONSTRAINT ck_lgd_variants_stock_version CHECK (stock >= 0 AND version > 0),
	CONSTRAINT ck_lgd_variants_identity_nonempty CHECK (btrim(size) <> '' AND btrim(color) <> '' AND btrim(normalized_size) <> '' AND btrim(normalized_color) <> ''),
	CONSTRAINT ck_lgd_variants_reference_cost_valid CHECK (reference_cost IS NULL OR (reference_cost >= 0 AND reference_cost <> 'NaN'::numeric)),
	CONSTRAINT ck_lgd_variants_reference_price_valid CHECK (reference_price IS NULL OR (reference_price >= 0 AND reference_price <> 'NaN'::numeric)),
	CONSTRAINT ck_lgd_variants_average_cost_valid CHECK (average_cost IS NULL OR (average_cost >= 0 AND average_cost <> 'NaN'::numeric)),
	CONSTRAINT fk_lgd_variants_product_id_lgd_products FOREIGN KEY(product_id) REFERENCES lgd_products (id) ON DELETE RESTRICT,
	CONSTRAINT uq_lgd_variants_code UNIQUE (code)
)""",
    """CREATE TABLE lgd_requests (
	key VARCHAR(100) NOT NULL,
	operation_id UUID NOT NULL,
	fingerprint VARCHAR(64) NOT NULL,
	response JSONB NOT NULL,
	document_version INTEGER DEFAULT '1' NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_lgd_requests PRIMARY KEY (key),
	CONSTRAINT ck_lgd_requests_key_fingerprint CHECK (length(key) > 0 AND fingerprint ~ '^[0-9a-f]{64}$'),
	CONSTRAINT ck_lgd_requests_document_valid CHECK (document_version > 0 AND jsonb_typeof(response) = 'object'),
	CONSTRAINT fk_lgd_requests_operation_id_lgd_operations FOREIGN KEY(operation_id) REFERENCES lgd_operations (id) ON DELETE RESTRICT
)""",
    """CREATE TABLE lgd_sale_payments (
	id UUID NOT NULL,
	operation_id UUID NOT NULL,
	operation_kind VARCHAR(20) DEFAULT 'sale' NOT NULL,
	position INTEGER NOT NULL,
	method_id UUID NOT NULL,
	amount NUMERIC(14, 2) NOT NULL,
	method_name VARCHAR(255) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_lgd_sale_payments PRIMARY KEY (id),
	CONSTRAINT uq_lgd_sale_payments_position UNIQUE (operation_id, position) DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT fk_lgd_sale_payments_operation_id_lgd_operations FOREIGN KEY(operation_id, operation_kind) REFERENCES lgd_operations (id, kind) ON DELETE RESTRICT,
	CONSTRAINT ck_lgd_sale_payments_sale_only CHECK (operation_kind = 'sale'),
	CONSTRAINT ck_lgd_sale_payments_amount_position CHECK (amount > 0 AND amount <> 'NaN'::numeric AND position >= 0),
	CONSTRAINT fk_lgd_sale_payments_method_id_lgd_payment_methods FOREIGN KEY(method_id) REFERENCES lgd_payment_methods (id) ON DELETE RESTRICT
)""",
    """CREATE TABLE lgd_photos (
	id UUID NOT NULL,
	product_id UUID NOT NULL,
	filename VARCHAR(100) NOT NULL,
	variant_id UUID,
	color VARCHAR(100),
	position INTEGER DEFAULT '0' NOT NULL,
	\"primary\" BOOLEAN DEFAULT false NOT NULL,
	CONSTRAINT pk_lgd_photos PRIMARY KEY (id),
	CONSTRAINT fk_lgd_photos_product_id_lgd_variants FOREIGN KEY(product_id, variant_id) REFERENCES lgd_variants (product_id, id) ON DELETE RESTRICT,
	CONSTRAINT ck_lgd_photos_position_nonnegative CHECK (position >= 0),
	CONSTRAINT fk_lgd_photos_product_id_lgd_products FOREIGN KEY(product_id) REFERENCES lgd_products (id) ON DELETE RESTRICT,
	CONSTRAINT uq_lgd_photos_filename UNIQUE (filename)
)""",
    """CREATE INDEX ix_lgd_photos_product_order ON lgd_photos (product_id, position, id)""",
    """CREATE UNIQUE INDEX uq_lgd_photos_primary ON lgd_photos (product_id) WHERE \"primary\"""",
    """CREATE TABLE lgd_movements (
	id UUID NOT NULL,
	operation_id UUID NOT NULL,
	variant_id UUID NOT NULL,
	version INTEGER NOT NULL,
	delta INTEGER NOT NULL,
	reason TEXT NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_lgd_movements PRIMARY KEY (id),
	CONSTRAINT ck_lgd_movements_version_delta CHECK (version > 0 AND delta <> 0),
	CONSTRAINT ck_lgd_movements_reason_nonempty CHECK (btrim(reason) <> ''),
	CONSTRAINT fk_lgd_movements_operation_id_lgd_operations FOREIGN KEY(operation_id) REFERENCES lgd_operations (id) ON DELETE RESTRICT,
	CONSTRAINT fk_lgd_movements_variant_id_lgd_variants FOREIGN KEY(variant_id) REFERENCES lgd_variants (id) ON DELETE RESTRICT
)""",
    """CREATE INDEX ix_lgd_movements_origin ON lgd_movements (operation_id, created_at, id)""",
    """CREATE INDEX ix_lgd_movements_variant_id ON lgd_movements (variant_id)""",
    """CREATE TABLE lgd_operation_items (
	operation_id UUID NOT NULL,
	position INTEGER NOT NULL,
	operation_kind VARCHAR(20) NOT NULL,
	variant_id UUID NOT NULL,
	quantity INTEGER NOT NULL,
	unit_cost NUMERIC(14, 2),
	unit_price NUMERIC(14, 2),
	snapshot JSONB NOT NULL,
	CONSTRAINT pk_lgd_operation_items PRIMARY KEY (operation_id, position),
	CONSTRAINT fk_lgd_operation_items_operation_id_lgd_operations FOREIGN KEY(operation_id, operation_kind) REFERENCES lgd_operations (id, kind) ON DELETE RESTRICT,
	CONSTRAINT uq_lgd_operation_items_operation_id UNIQUE (operation_id, variant_id),
	CONSTRAINT ck_lgd_operation_items_quantity_position CHECK (position >= 0 AND quantity > 0),
	CONSTRAINT ck_lgd_operation_items_cost_valid CHECK (unit_cost IS NULL OR (unit_cost >= 0 AND unit_cost <> 'NaN'::numeric)),
	CONSTRAINT ck_lgd_operation_items_values_match_kind CHECK ((operation_kind = 'sale' AND unit_price IS NOT NULL AND unit_price > 0 AND unit_price <> 'NaN'::numeric AND unit_cost IS NULL) OR (operation_kind = 'purchase' AND unit_price IS NULL AND unit_cost IS NOT NULL AND unit_cost > 0) OR (operation_kind IN ('inventory','adjustment') AND unit_price IS NULL)),
	CONSTRAINT ck_lgd_operation_items_snapshot_object CHECK (jsonb_typeof(snapshot) = 'object'),
	CONSTRAINT fk_lgd_operation_items_variant_id_lgd_variants FOREIGN KEY(variant_id) REFERENCES lgd_variants (id) ON DELETE RESTRICT
)""",
]


def upgrade():
    if not op.get_context().as_sql:
        existing = set(inspect(op.get_bind()).get_table_names(schema="public")) - {
            "alembic_version"
        }
        if existing:
            raise RuntimeError("Baseline exige schema vazio; nenhum dado será convertido")
    for statement in DDL:
        op.execute(statement)
    op.execute("GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO lgd_app")
    op.execute("REVOKE INSERT ON alembic_version FROM lgd_app")
    op.execute(
        "GRANT UPDATE ON lgd_control, lgd_suppliers, lgd_categories, lgd_purchase_channels, lgd_sale_channels, lgd_payment_methods, lgd_products, lgd_variants, lgd_photos, lgd_operations, lgd_operation_items, lgd_sale_payments TO lgd_app"
    )
    op.execute("GRANT DELETE ON lgd_photos, lgd_operation_items, lgd_sale_payments TO lgd_app")


def downgrade():
    for table in [
        "lgd_requests",
        "lgd_revisions",
        "lgd_movements",
        "lgd_sale_payments",
        "lgd_operation_items",
        "lgd_operations",
        "lgd_photos",
        "lgd_variants",
        "lgd_products",
        "lgd_payment_methods",
        "lgd_sale_channels",
        "lgd_purchase_channels",
        "lgd_categories",
        "lgd_suppliers",
        "lgd_control",
    ]:
        op.drop_table(table)
