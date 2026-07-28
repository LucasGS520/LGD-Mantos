"""publishing_status_sem_estado_morto

Remove o valor 'waiting_approval' do enum publishing_status. O estado nunca foi
usado de verdade: itens só entram na fila DEPOIS da aprovação humana (o
PolicyEngine valida no enfileiramento), então o ciclo real é
approved → published | failed.

O Postgres não permite remover valor de enum diretamente — a técnica é criar um
tipo novo, converter a coluna e descartar o tipo antigo.

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-16 23:20:00.000000

"""
from typing import Sequence, Union

from alembic import op


# Identificadores desta revision, usados pelo Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Realoca eventuais linhas no estado morto (não deve existir nenhuma).
    op.execute(
        "UPDATE publishing_queue SET status = 'approved' "
        "WHERE status = 'waiting_approval'"
    )
    op.execute("ALTER TYPE publishing_status RENAME TO publishing_status_old")
    op.execute(
        "CREATE TYPE publishing_status AS ENUM ('approved', 'published', 'failed')"
    )
    op.execute(
        "ALTER TABLE publishing_queue ALTER COLUMN status "
        "TYPE publishing_status USING status::text::publishing_status"
    )
    op.execute("DROP TYPE publishing_status_old")


def downgrade() -> None:
    # Restaura o tipo original com o valor 'waiting_approval'.
    op.execute("ALTER TYPE publishing_status RENAME TO publishing_status_old")
    op.execute(
        "CREATE TYPE publishing_status AS ENUM "
        "('waiting_approval', 'approved', 'published', 'failed')"
    )
    op.execute(
        "ALTER TABLE publishing_queue ALTER COLUMN status "
        "TYPE publishing_status USING status::text::publishing_status"
    )
    op.execute("DROP TYPE publishing_status_old")
