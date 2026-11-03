"""Classifica produtos em situações de estoque, margem e giro.

Migrado de `analytics.services.product_classification_service` na Fase 3
(Task 3): o Motor de Sinais é quem consome isto agora — `stock_rules.py` e
`product_rules.py` leem estas mesmas cinco listas via `SignalContext.classificacao`
para decidir quais viram sinal. A lógica em si NÃO mudou nesta migração: mesmos
limiares, mesmas condições, mesma ordenação — só o módulo que a hospeda.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repositories import product_repository as product_repo
from app.modules.analytics.repositories import sales_repository as sales_repo
from app.modules.settings.service import PreferenceService

# Constantes de classificação — não fazem parte dos dez limiares configuráveis
# em Settings (ver `app.modules.settings.service`). São parâmetros da lógica de
# classificação em si, não algo que o dono calibra pela tela. `MARGIN_HIGH` é
# reaproveitado por `rules/product_rules.py` no texto da regra `margem_alta`,
# por isso não leva underscore — é usado fora deste módulo.
STOCK_SAFE = 5      # estoque mínimo para considerar a disponibilidade saudável
VELOCITY_MIN = 3    # unidades/30d para considerar o produto de alta saída
MARGIN_HIGH = 35.0  # margem % a partir da qual o produto é de margem alta


async def classificar_produtos(db: AsyncSession) -> dict:
    """Devolve as cinco situações de estoque/margem/giro usadas pelo Motor de Sinais.

    Uma variante entra em no máximo uma das cinco listas, exceto quando cai no
    ramo `else` (nem sem estoque nem crítico) — aí pode entrar em várias das
    três listas informativas (alta saída, margem alta, encalhado) ao mesmo
    tempo, já que são recortes independentes sobre a mesma variante.
    """

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
        elif sold >= VELOCITY_MIN and stock <= prefs.critical_stock:
            estoque_critico.append({**item, "reason": "boa saída, estoque crítico"})
        else:
            if sold >= VELOCITY_MIN and stock >= STOCK_SAFE:
                alta_saida_estoque_saudavel.append(
                    {**item, "reason": "alta saída e estoque saudável"}
                )
            if margin_pct >= MARGIN_HIGH and stock >= STOCK_SAFE:
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
    # regra em dois lugares criaria duas fontes de verdade para o mesmo
    # conceito. No Motor de Sinais, `stock_rules.produto_parado` lê essa
    # mesma chave via `SignalContext.produtos`.
    return {
        "alta_saida_estoque_saudavel": alta_saida_estoque_saudavel,
        "margem_alta": margem_alta,
        "baixa_saida_estoque_alto": baixa_saida_estoque_alto,
        "estoque_critico": estoque_critico,
        "sem_estoque": sem_estoque,
    }
