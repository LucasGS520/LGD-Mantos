"""Serviço de leitura e gravação das preferências de alerta do sistema.

Regra de negócio: existe no máximo um registro de preferências (id fixo 1).
A leitura nunca escreve no banco — quando o registro ainda não existe, devolve
um objeto transiente com os valores padrão, deixando a tabela vazia até a
primeira gravação real feita pelo operador.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.common import now
from app.shared.models.settings import AppPreference
from app.modules.settings.schemas import PreferencesUpdate

_SINGLETON_ID = 1
_DEFAULTS = {"rupture_days": 15, "stopped_days": 60, "critical_stock": 3}


class PreferenceService:
    """Centraliza acesso ao registro único de preferências de alerta."""

    @staticmethod
    async def get(db: AsyncSession) -> AppPreference:
        """Retorna as preferências vigentes, ou os padrões se nada foi salvo ainda.

        Usado pela rota de Configurações — se o banco falhar aqui, o erro deve
        aparecer para o operador (ele está tentando ver/editar a própria
        configuração), não ser mascarado silenciosamente.
        """

        pref = await db.get(AppPreference, _SINGLETON_ID)
        if pref is None:
            return AppPreference(id=_SINGLETON_ID, updated_at=now(), **_DEFAULTS)
        return pref

    @staticmethod
    async def get_safe(db: AsyncSession) -> AppPreference:
        """Como get(), mas nunca propaga erro — cai para os padrões em qualquer falha.

        Usado pelas análises operacionais (risco de ruptura, produtos parados,
        estoque crítico): a tabela de preferências ficar momentaneamente
        inacessível não pode derrubar a análise inteira, que continua útil
        mesmo usando os limiares padrão.
        """

        try:
            return await PreferenceService.get(db)
        except Exception:
            # Deixa a sessão limpa para as consultas seguintes da mesma requisição
            # não herdarem uma transação já abortada pelo erro acima.
            try:
                await db.rollback()
            except Exception:
                pass
            return AppPreference(id=_SINGLETON_ID, updated_at=now(), **_DEFAULTS)

    @staticmethod
    async def update(db: AsyncSession, data: PreferencesUpdate) -> AppPreference:
        """Grava os limiares informados, criando o registro único na primeira vez (upsert)."""

        pref = await db.get(AppPreference, _SINGLETON_ID)
        if pref is None:
            pref = AppPreference(id=_SINGLETON_ID)
            db.add(pref)
        pref.rupture_days = data.rupture_days
        pref.stopped_days = data.stopped_days
        pref.critical_stock = data.critical_stock
        pref.updated_at = now()
        await db.flush()
        return pref
