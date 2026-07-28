"""Testes do PublishingService — fila de publicação com fechamento manual.

Cobrem a barreira de aprovação humana no enfileiramento e as transições de
estado do ciclo: approved → published (com published_at) e o cancelamento.
"""

import pytest
from fastapi import HTTPException

from app.modules.agents.approval.service import ApprovalService
from app.modules.agents.publishing.service import PublishingService
from tests.conftest import create_campaign_bundle


class TestEnfileirar:
    async def test_bloqueia_campanha_sem_aprovacao(self, db):
        _, campaign, _, _, approval = await create_campaign_bundle(db)
        # Aprovação existe mas está pendente — publicar exige 'approved'.
        with pytest.raises(HTTPException) as exc:
            await PublishingService.queue_campaign(db, campaign.id, "Instagram")
        assert exc.value.status_code == 403

    async def test_enfileira_campanha_aprovada(self, db):
        _, campaign, _, _, approval = await create_campaign_bundle(db)
        await ApprovalService.approve(db, approval.id)

        entry = await PublishingService.queue_campaign(db, campaign.id, "Instagram")
        assert entry.status == "approved"
        assert entry.published_at is None

    async def test_campanha_inexistente_retorna_404(self, db):
        with pytest.raises(HTTPException) as exc:
            await PublishingService.queue_campaign(
                db, "00000000-0000-0000-0000-000000000000", "Instagram"
            )
        assert exc.value.status_code == 404


class TestMarcarPublicado:
    async def _entry_aprovada(self, db):
        _, campaign, _, _, approval = await create_campaign_bundle(db)
        await ApprovalService.approve(db, approval.id)
        return await PublishingService.queue_campaign(db, campaign.id, "Instagram")

    async def test_publica_e_grava_published_at(self, db):
        entry = await self._entry_aprovada(db)
        publicado = await PublishingService.mark_published(db, entry.id)
        assert publicado.status == "published"
        assert publicado.published_at is not None

    async def test_nao_publica_duas_vezes(self, db):
        entry = await self._entry_aprovada(db)
        await PublishingService.mark_published(db, entry.id)
        with pytest.raises(HTTPException) as exc:
            await PublishingService.mark_published(db, entry.id)
        assert exc.value.status_code == 409

    async def test_item_inexistente_retorna_404(self, db):
        with pytest.raises(HTTPException) as exc:
            await PublishingService.mark_published(db, "00000000-0000-0000-0000-000000000000")
        assert exc.value.status_code == 404


class TestRemover:
    async def test_remove_item_nao_publicado(self, db):
        _, campaign, _, _, approval = await create_campaign_bundle(db)
        await ApprovalService.approve(db, approval.id)
        entry = await PublishingService.queue_campaign(db, campaign.id, "Instagram")

        await PublishingService.remove_from_queue(db, entry.id)
        assert await PublishingService.list_queue(db) == []

    async def test_nao_remove_item_publicado(self, db):
        _, campaign, _, _, approval = await create_campaign_bundle(db)
        await ApprovalService.approve(db, approval.id)
        entry = await PublishingService.queue_campaign(db, campaign.id, "Instagram")
        await PublishingService.mark_published(db, entry.id)

        with pytest.raises(HTTPException) as exc:
            await PublishingService.remove_from_queue(db, entry.id)
        assert exc.value.status_code == 409
