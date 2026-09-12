"""remove_marketing

Remove o domínio de Marketing por completo: as sete tabelas do workspace de
agentes (runs, campanhas, posts, briefings criativos, aprovações, fila de
publicação e documentos de conhecimento) e os cinco tipos enum que só elas
usavam.

Esta migration é irreversível quanto a DADOS. O downgrade() recria a estrutura
vazia para manter a cadeia de revisions navegável, mas não recupera conteúdo.
Exportar o que for relevante antes de aplicar em produção.

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# Identificadores desta revision, usados pelo Alembic.
revision: str = '0005'
down_revision: Union[str, None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Tabelas na ordem de remoção — filhas antes das pais, por causa das FKs.
TABELAS = [
    'approvals',
    'creative_briefs',
    'posts',
    'publishing_queue',
    'campaigns',
    'agent_runs',
    'knowledge_documents',
]

# Tipos enum criados junto com as tabelas acima. O Postgres não os remove
# automaticamente no DROP TABLE, então precisam de DROP TYPE explícito.
ENUMS = [
    'agent_run_status',
    'content_status',
    'approval_status',
    'publishing_status',
    'knowledge_doc_type',
]


def upgrade() -> None:
    for tabela in TABELAS:
        op.execute(f'DROP TABLE IF EXISTS {tabela} CASCADE')
    for enum in ENUMS:
        op.execute(f'DROP TYPE IF EXISTS {enum}')


def downgrade() -> None:
    """Recria a estrutura vazia. Não restaura dados."""
    agent_run_status = postgresql.ENUM(
        'pending', 'running', 'completed', 'failed', name='agent_run_status',
    )
    content_status = postgresql.ENUM(
        'draft', 'pending_approval', 'approved', 'rejected', name='content_status',
    )
    approval_status = postgresql.ENUM(
        'pending', 'approved', 'rejected', 'revision_requested', name='approval_status',
    )
    publishing_status = postgresql.ENUM(
        'approved', 'published', 'failed', name='publishing_status',
    )
    knowledge_doc_type = postgresql.ENUM(
        'brand_voice', 'persona', 'commercial_rules', 'visual_reference',
        'approved_caption', 'approved_prompt', 'campaign_context',
        'product_style_notes', name='knowledge_doc_type',
    )

    bind = op.get_bind()
    for enum in (agent_run_status, content_status, approval_status,
                 publishing_status, knowledge_doc_type):
        enum.create(bind, checkfirst=True)

    op.create_table(
        'agent_runs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('objective', sa.Text(), nullable=False),
        sa.Column('status', agent_run_status, nullable=False),
        sa.Column('result', postgresql.JSONB(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'knowledge_documents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('doc_type', knowledge_doc_type, nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'campaigns',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('agent_run_id', sa.String(36), sa.ForeignKey('agent_runs.id')),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('objective', sa.Text(), nullable=True),
        sa.Column('product_id', sa.String(36), nullable=True),
        sa.Column('channel', sa.String(50), nullable=True),
        sa.Column('format', sa.String(50), nullable=True),
        sa.Column('angle', sa.Text(), nullable=True),
        sa.Column('cta', sa.String(200), nullable=True),
        sa.Column('risk_level', sa.String(20), nullable=True),
        sa.Column('status', content_status, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'posts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id')),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('headline', sa.String(200), nullable=True),
        sa.Column('cta_text', sa.String(200), nullable=True),
        sa.Column('format', sa.String(50), nullable=True),
        sa.Column('copy_variations', postgresql.JSONB(), nullable=True),
        sa.Column('status', content_status, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'creative_briefs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id')),
        sa.Column('visual_briefing', sa.Text(), nullable=True),
        sa.Column('image_prompt', sa.Text(), nullable=True),
        sa.Column('status', content_status, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'approvals',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id')),
        sa.Column('status', approval_status, nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'publishing_queue',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id')),
        sa.Column('channel', sa.String(50), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', publishing_status, nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
