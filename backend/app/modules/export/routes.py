"""Rotas de exportação de dados — backup manual do operador em CSV/ZIP."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.modules.export.service import EXPORT_SETS, ExportService

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/backup")
async def export_backup(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Baixa um .zip com um CSV por conjunto — backup completo em um único arquivo.

    Registrada antes de `/{dataset}` para que "backup" nunca seja interpretado
    como nome de conjunto pela rota genérica abaixo.
    """

    content = await ExportService.export_backup(db)
    filename = f"lgd-backup-{date.today().isoformat()}.zip"
    return Response(
        content=content,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{dataset}")
async def export_dataset(dataset: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    """Baixa o CSV de um conjunto (produtos, vendas, compras, despesas, movimentacoes, cadastros)."""

    try:
        content = await ExportService.export_set(db, dataset)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Conjunto invalido. Use um de: {', '.join(EXPORT_SETS)}",
        )
    filename = f"lgd-{dataset}-{date.today().isoformat()}.csv"
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
