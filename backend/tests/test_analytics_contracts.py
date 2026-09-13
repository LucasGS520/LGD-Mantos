"""Contrato dos endpoints de Analytics que sobrevivem à Fase 1.

Estes testes não validam valores calculados — validam que cada rota existe,
exige autenticação e devolve a estrutura que o frontend consome. Servem de rede
de segurança para as fases seguintes, que vão mexer nesses mesmos services.
"""

import pytest


ROTAS_PROTEGIDAS = [
    "/api/v1/analytics/dashboard",
    "/api/v1/analytics/top-products",
    "/api/v1/analytics/by-size",
    "/api/v1/analytics/by-channel",
    "/api/v1/analytics/products/analysis",
    "/api/v1/analytics/data-quality",
    "/api/v1/analytics/finance/dre",
    "/api/v1/analytics/categories/performance",
    "/api/v1/analytics/categories/stock-coverage",
    "/api/v1/analytics/categories/size-distribution",
    "/api/v1/analytics/categories/buying-patterns",
    "/api/v1/analytics/categories/size-stock",
    "/api/v1/analytics/products/attributes",
    "/api/v1/analytics/product-classification",
]


@pytest.mark.parametrize("rota", ROTAS_PROTEGIDAS)
async def test_rota_exige_autenticacao(client, rota):
    resposta = await client.get(rota)
    assert resposta.status_code == 403, f"{rota} respondeu {resposta.status_code}"


@pytest.mark.parametrize("rota", ROTAS_PROTEGIDAS)
async def test_rota_responde_200_autenticada(auth_client, rota):
    resposta = await auth_client.get(rota)
    assert resposta.status_code == 200, f"{rota}: {resposta.text}"


async def test_dashboard_expoe_os_campos_consumidos_pelo_frontend(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/dashboard")
    corpo = resposta.json()
    for campo in (
        "today_revenue", "today_count", "month_revenue", "month_cogs",
        "month_expenses", "gross_profit", "net_profit", "margin_pct",
        "avg_ticket", "total_units_sold", "stock_cost_value",
        "stock_sale_value", "stock_units", "daily_revenue",
    ):
        assert campo in corpo, f"campo ausente no dashboard: {campo}"
    assert len(corpo["daily_revenue"]) == 30


async def test_product_analysis_expoe_as_listas_consumidas_pelo_frontend(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/products/analysis")
    corpo = resposta.json()
    for chave in ("rupture_risk", "stopped"):
        assert chave in corpo, f"chave ausente na analise de produtos: {chave}"
        assert isinstance(corpo[chave], list)


async def test_data_quality_expoe_score_e_total(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/data-quality")
    corpo = resposta.json()
    assert "score" in corpo
    assert "total_issues" in corpo


# --- Fase 2: comparação com o período anterior (?compare=true) ---------------


async def test_dashboard_sem_compare_nao_traz_comparacao(auth_client):
    """Compatibilidade retroativa: o payload padrão não muda de forma."""
    resposta = await auth_client.get("/api/v1/analytics/dashboard")
    assert "comparacao" not in resposta.json()


async def test_dashboard_com_compare_traz_os_indicadores_comparados(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/dashboard?compare=true")
    comparacao = resposta.json()["comparacao"]
    for indicador in (
        "month_revenue", "gross_profit", "net_profit",
        "margin_pct", "avg_ticket", "total_units_sold",
    ):
        assert indicador in comparacao, f"indicador ausente: {indicador}"
        assert set(comparacao[indicador]) == {"atual", "anterior", "variacao_pct"}


async def test_product_analysis_sem_compare_nao_traz_comparacao(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/products/analysis")
    assert "comparacao" not in resposta.json()


async def test_product_analysis_com_compare_traz_contagens_comparadas(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/products/analysis?compare=true")
    comparacao = resposta.json()["comparacao"]
    for indicador in ("rupture_risk", "stopped"):
        assert indicador in comparacao, f"indicador ausente: {indicador}"
        assert set(comparacao[indicador]) == {"atual", "anterior", "variacao_pct"}


async def test_by_channel_sem_compare_continua_uma_lista(auth_client):
    """Sem compare, /by-channel continua devolvendo a lista de sempre (não um objeto)."""
    resposta = await auth_client.get("/api/v1/analytics/by-channel")
    assert isinstance(resposta.json(), list)


async def test_by_channel_com_compare_traz_lista_e_comparacao(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/by-channel?compare=true")
    corpo = resposta.json()
    assert isinstance(corpo["channels"], list)
    for indicadores in corpo["comparacao"].values():
        assert set(indicadores) == {"total", "count"}
        for indicador in indicadores.values():
            assert set(indicador) == {"atual", "anterior", "variacao_pct"}


async def test_dre_sem_compare_nao_traz_comparacao(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/finance/dre")
    assert "comparacao" not in resposta.json()


async def test_dre_com_compare_traz_os_indicadores_comparados(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/finance/dre?compare=true")
    comparacao = resposta.json()["comparacao"]
    for indicador in (
        "revenue", "cogs", "gross_profit", "gross_margin_pct",
        "expenses", "net_profit", "margin_pct",
    ):
        assert indicador in comparacao, f"indicador ausente: {indicador}"
        assert set(comparacao[indicador]) == {"atual", "anterior", "variacao_pct"}
