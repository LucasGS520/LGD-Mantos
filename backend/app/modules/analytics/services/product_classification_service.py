"""Classifica produtos em situações de estoque para apoiar decisões de compra e giro."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import product_repository as product_repo
from app.modules.analytics.repositories import sales_repository as sales_repo
from app.modules.settings.service import PreferenceService

_STOCK_SAFE = 5      # estoque mínimo para considerar a disponibilidade saudável
_VELOCITY_MIN = 3    # unidades/30d para considerar o produto de alta saída
_MARGIN_HIGH = 35.0  # margem % a partir da qual o produto é de margem alta


class ProductClassificationService:
    @staticmethod
    async def product_classification(db: AsyncSession) -> dict:
        # O limiar de estoque crítico é configurável pelo operador na tela de
        # Configurações — ver app.modules.settings.
        prefs = await PreferenceService.get_safe(db)
        since_30 = datetime.now(timezone.utc) - timedelta(days=30)
        velocity = await sales_repo.variant_velocity_30d(db, since_30)
        variants = await product_repo.active_variants(db)

        sem_estoque: list[dict] = []
        estoque_critico: list[dict] = []
        alta_saida_estoque_saudavel: list[dict] = []
        margem_alta: list[dict] = []
        baixa_saida_estoque_alto: list[dict] = []

        for variant in variants:
            sold = velocity.get(variant.id, 0)
            stock = variant.stock_quantity
            sale_price = float(variant.product.sale_price or 0)
            cost_price = float(variant.product.cost_price or 0)
            margin_pct = (
                round((sale_price - cost_price) / sale_price * 100, 1)
                if sale_price > 0
                else 0.0
            )

            item = {
                "product_name": variant.product.name,
                "sku": variant.product.sku,
                "size": variant.size,
                "color": variant.color,
                "stock": stock,
                "margin_pct": margin_pct,
                "sold_30d": sold,
            }

            if stock == 0:
                sem_estoque.append({**item, "reason": "sem estoque"})
            elif sold >= _VELOCITY_MIN and stock <= prefs.critical_stock:
                estoque_critico.append({**item, "reason": "boa saída, estoque crítico"})
            else:
                if sold >= _VELOCITY_MIN and stock >= _STOCK_SAFE:
                    alta_saida_estoque_saudavel.append(
                        {**item, "reason": "alta saída e estoque saudável"}
                    )
                if margin_pct >= _MARGIN_HIGH and stock >= _STOCK_SAFE:
                    margem_alta.append({**item, "reason": "margem alta e disponível"})
                if sold == 0 and stock > 0:
                    baixa_saida_estoque_alto.append(
                        {**item, "reason": "sem saída no período — estoque encalhado"}
                    )

        alta_saida_estoque_saudavel.sort(key=lambda x: x["sold_30d"], reverse=True)
        margem_alta.sort(key=lambda x: x["margin_pct"], reverse=True)
        baixa_saida_estoque_alto.sort(key=lambda x: x["stock"], reverse=True)
        estoque_critico.sort(key=lambda x: x["sold_30d"], reverse=True)

        # A sexta situação de estoque — produto parado — NÃO é calculada aqui.
        # Ela já existe em ProductAnalysisService.product_analysis sob a chave
        # `stopped`, com janela configurável (prefs.stopped_days). Duplicar a
        # regra em dois services criaria duas fontes de verdade para o mesmo
        # conceito. O frontend lê essa situação de /analytics/products/analysis.
        return {
            "alta_saida_estoque_saudavel": alta_saida_estoque_saudavel,
            "margem_alta": margem_alta,
            "baixa_saida_estoque_alto": baixa_saida_estoque_alto,
            "estoque_critico": estoque_critico,
            "sem_estoque": sem_estoque,
        }
