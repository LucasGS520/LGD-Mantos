"""preferencias_de_alerta

Cria a tabela app_preferences: registro único (id sempre 1, garantido por
CHECK) com os limiares de alerta que hoje estavam cravados no código
(rupture_days, stopped_days, critical_stock). Passam a ser configuráveis
pela tela de Configurações sem exigir deploy.

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Identificadores desta revision, usados pelo Alembic.
revision: str = '0004'
down_revision: Union[str, None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'app_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rupture_days', sa.Integer(), nullable=False),
        sa.Column('stopped_days', sa.Integer(), nullable=False),
        sa.Column('critical_stock', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('id = 1', name='ck_app_preferences_singleton'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('app_preferences')
