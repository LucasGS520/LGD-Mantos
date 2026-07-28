"""Testes do ApprovalService — o human-in-the-loop da camada de agentes.

Cobrem o efeito cascata das decisões sobre Campaign/Post/Brief, a exigência de
comentário e a proibição de re-decidir uma aprovação já decidida.
"""

import pytest
from fastapi import HTTPException

from app.modules.agents.approval.service import ApprovalService
from tests.conftest import create_campaign_bundle, create_product


class TestAprovar:
    async def test_aprova_com_cascata(self, db):
        _, campaign, post, brief, approval = await create_campaign_bundle(db)
        resultado = await ApprovalService.approve(db, approval.id, comment="ok")

        assert resultado.status == "approved"
        assert resultado.decided_at is not None
        await db.refresh(campaign)
        await db.refresh(post)
        await db.refresh(brief)
        assert campaign.status == "approved"
        assert post.status == "approved"
        assert brief.status == "approved"

    async def test_nao_permite_redecisao(self, db):
        _, _, _, _, approval = await create_campaign_bundle(db)
        await ApprovalService.approve(db, approval.id)

        with pytest.raises(HTTPException) as exc:
            await ApprovalService.approve(db, approval.id)
        assert exc.value.status_code == 409


class TestRejeitar:
    async def test_comentario_obrigatorio(self, db):
        _, _, _, _, approval = await create_campaign_bundle(db)
        with pytest.raises(HTTPException) as exc:
            await ApprovalService.reject(db, approval.id, comment="   ")
        assert exc.value.status_code == 422

    async def test_rejeita_com_cascata(self, db):
        _, campaign, post, brief, approval = await create_campaign_bundle(db)
        resultado = await ApprovalService.reject(db, approval.id, comment="Fora do tom")

        assert resultado.status == "rejected"
        await db.refresh(campaign)
        await db.refresh(post)
        await db.refresh(brief)
        assert campaign.status == "rejected"
        assert post.status == "rejected"
        assert brief.status == "rejected"


class TestRevisao:
    async def test_comentario_obrigatorio(self, db):
        _, _, _, _, approval = await create_campaign_bundle(db)
        with pytest.raises(HTTPException) as exc:
            await ApprovalService.request_revision(db, approval.id, comment="")
        assert exc.value.status_code == 422

    async def test_revisao_volta_artefatos_para_draft(self, db):
        _, campaign, post, brief, approval = await create_campaign_bundle(db)
        resultado = await ApprovalService.request_revision(
            db, approval.id, comment="Deixe a legenda mais curta"
        )

        assert resultado.status == "revision_requested"
        assert resultado.comment == "Deixe a legenda mais curta"
        await db.refresh(campaign)
        await db.refresh(post)
        await db.refresh(brief)
        assert campaign.status == "draft"
        assert post.status == "draft"
        assert brief.status == "draft"


class TestLeitura:
    async def test_detail_inexistente_retorna_404(self, db):
        with pytest.raises(HTTPException) as exc:
            await ApprovalService.get_detail(db, "00000000-0000-0000-0000-000000000000")
        assert exc.value.status_code == 404

    async def test_list_pending_filtra_por_status(self, db):
        _, _, _, _, approval = await create_campaign_bundle(db)
        pendentes = await ApprovalService.list_pending(db)
        assert [a.id for a in pendentes] == [approval.id]

        await ApprovalService.approve(db, approval.id)
        assert await ApprovalService.list_pending(db) == []
