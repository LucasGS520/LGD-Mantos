"""Classificação de produtos em situações de estoque.

O service cruza velocidade de venda em 30 dias, estoque e margem para dizer em
que situação cada variante está. É a lógica que a Fase 3 vai transformar em
regras do Motor de Sinais — aqui ela só perde o vocabulário de marketing.
"""

from tests.conftest import create_product


CHAVES_ESPERADAS = {
    "alta_saida_estoque_saudavel",
    "margem_alta",
    "baixa_saida_estoque_alto",
    "estoque_critico",
    "sem_estoque",
}


async def test_endpoint_responde_com_as_cinco_situacoes(auth_client):
    resposta = await auth_client.get("/api/v1/analytics/product-classification")
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert set(corpo.keys()) == CHAVES_ESPERADAS
    for chave in CHAVES_ESPERADAS:
        assert isinstance(corpo[chave], list), f"{chave} deveria ser lista"


async def test_produto_sem_estoque_cai_em_sem_estoque(auth_client, db):
    await create_product(db, sku="ZERADO", name="Manto Zerado", stock=0)
    resposta = await auth_client.get("/api/v1/analytics/product-classification")
    skus = [item["sku"] for item in resposta.json()["sem_estoque"]]
    assert "ZERADO" in skus


async def test_produto_sem_saida_com_estoque_cai_em_baixa_saida(auth_client, db):
    await create_product(db, sku="PARADO", name="Manto Parado", stock=12)
    resposta = await auth_client.get("/api/v1/analytics/product-classification")
    skus = [item["sku"] for item in resposta.json()["baixa_saida_estoque_alto"]]
    assert "PARADO" in skus


async def test_produto_margem_alta_e_disponivel_cai_em_margem_alta(auth_client, db):
    """create_product usa cost_price=80.0 e sale_price=199.9 (margem ~60%,
    acima de _MARGIN_HIGH=35.0). Com stock=5 (padrão) satisfaz _STOCK_SAFE e,
    sem venda registrada, sold_30d=0 — o produto cai tanto em margem_alta
    quanto em baixa_saida_estoque_alto, já que as listas não são exclusivas.
    """
    await create_product(db, sku="MARGEM", name="Manto Margem")
    resposta = await auth_client.get("/api/v1/analytics/product-classification")
    skus = [item["sku"] for item in resposta.json()["margem_alta"]]
    assert "MARGEM" in skus


async def test_item_classificado_traz_os_campos_consumidos_pelo_frontend(auth_client, db):
    await create_product(db, sku="CAMPOS", name="Manto Campos", stock=0)
    resposta = await auth_client.get("/api/v1/analytics/product-classification")
    item = resposta.json()["sem_estoque"][0]
    for campo in ("product_name", "sku", "size", "color", "stock",
                  "margin_pct", "sold_30d", "reason"):
        assert campo in item, f"campo ausente no item classificado: {campo}"
