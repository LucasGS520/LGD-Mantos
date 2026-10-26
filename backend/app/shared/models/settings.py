"""Modelo ORM das preferências configuráveis do sistema.

Guarda os limiares de alerta que hoje ficariam cravados no código (dias para
risco de ruptura, dias para produto parado, estoque crítico de reposição),
permitindo que o operador os ajuste pela tela de Configurações sem precisar
de deploy.
"""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.models.common import now


class AppPreference(Base):
    """Preferências de alerta do sistema — registro único (id sempre 1).

    O CHECK de singleton garante que nunca exista mais de uma linha: leitura
    e gravação sempre miram o mesmo registro, sem ambiguidade sobre "qual
    configuração vale".
    """

    __tablename__ = "app_preferences"
    __table_args__ = (CheckConstraint("id = 1", name="ck_app_preferences_singleton"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    rupture_days: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    stopped_days: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    critical_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
