"""Testes das 15 regras do Motor de Sinais (Fase 3, Task 3).

Cada regra tem dois testes: um que prova que ela dispara quando deve (o
cenário que a Regra 3 da spec pede) e um que prova que ela NÃO dispara quando
não deve — esse segundo é o que pega regra grudada em verdadeiro, que passa
no caso feliz e depois acende pra sempre.

Contexto sempre sintético, montado à mão — nenhum teste aqui toca o banco.
Se uma regra precisasse de banco pra ser testada, a regra estaria impura.
"""

from app.modules.intelligence.services.product_classification import MARGIN_HIGH
from app.modules.intelligence.signals.rules import channel_rules, data_rules, finance_rules, product_rules, stock_rules
from app.modules.intelligence.signals.types import Area, Severidade, SignalContext

# Os dez limiares padrão do Motor de Sinais (ver task-3-brief.md) — usados tal
# qual em todos os testes, já que nenhuma regra pode cravar um limiar próprio.
LIMIARES = {
    "rupture_days": 15,
    "stopped_days": 60,
    "critical_stock": 3,
    "queda_atencao_pct": 10,
    "queda_critica_pct": 20,
    "margem_queda_atencao_pp": 3,
    "margem_queda_critica_pp": 7,
    "margem_minima_pct": 25,
    "despesa_alta_atencao_pct": 15,
    "qualidade_minima_pct": 80,
}


def _ctx(**overrides) -> SignalContext:
    """Monta um `SignalContext` sintético, com os campos vazios por padrão.

    Cada teste sobrescreve só o que precisa — o resto fica no "estado neutro"
    (dicts/listas vazias) que nenhuma regra deveria acender.
    """
    base = {
        "dashboard": {},
        "produtos": {},
        "classificacao": {},
        "canais": [],
        "qualidade": {},
        "limiares": LIMIARES,
    }
    base.update(overrides)
    return SignalContext(**base)


# ---------------------------------------------------------------------------
# finance_rules
# ---------------------------------------------------------------------------


def test_receita_em_queda_dispara_com_queda_acima_do_limiar():
    ctx = _ctx(dashboard={
        "comparacao": {"month_revenue": {"atual": 8500.0, "anterior": 10000.0, "variacao_pct": -15.0}}
    })
    sinal = finance_rules.receita_em_queda(ctx)
    assert sinal is not None
    assert sinal.codigo == "receita_em_queda"
    assert sinal.area is Area.FINANCEIRO
    assert sinal.severidade is Severidade.ATENCAO
    assert "15,0%" in sinal.diagnostico
    assert "R$ 8.500,00" in sinal.diagnostico
    assert "R$ 10.000,00" in sinal.diagnostico
    assert sinal.recomendacao is not None


def test_receita_em_queda_nao_dispara_com_queda_abaixo_do_limiar():
    ctx = _ctx(dashboard={
        "comparacao": {"month_revenue": {"atual": 9700.0, "anterior": 10000.0, "variacao_pct": -3.0}}
    })
    assert finance_rules.receita_em_queda(ctx) is None


def test_lucro_em_queda_dispara_e_marca_critico_acima_do_limiar_critico():
    ctx = _ctx(dashboard={
        "comparacao": {"net_profit": {"atual": 1600.0, "anterior": 2000.0, "variacao_pct": -20.0}}
    })
    sinal = finance_rules.lucro_em_queda(ctx)
    assert sinal is not None
    assert sinal.codigo == "lucro_em_queda"
    assert sinal.severidade is Severidade.CRITICO
    assert "20,0%" in sinal.diagnostico


def test_lucro_em_queda_nao_dispara_quando_lucro_sobe():
    ctx = _ctx(dashboard={
        "comparacao": {"net_profit": {"atual": 2500.0, "anterior": 2000.0, "variacao_pct": 25.0}}
    })
    assert finance_rules.lucro_em_queda(ctx) is None


def test_margem_em_queda_dispara_com_queda_em_pontos_percentuais():
    ctx = _ctx(dashboard={
        "comparacao": {"margin_pct": {"atual": 21.0, "anterior": 25.0, "variacao_pct": -16.0}}
    })
    sinal = finance_rules.margem_em_queda(ctx)
    assert sinal is not None
    assert sinal.codigo == "margem_em_queda"
    assert sinal.severidade is Severidade.ATENCAO
    assert "4,0" in sinal.diagnostico  # 25 - 21 = 4 pontos percentuais


def test_margem_em_queda_nao_dispara_com_queda_pequena():
    ctx = _ctx(dashboard={
        "comparacao": {"margin_pct": {"atual": 24.0, "anterior": 25.0, "variacao_pct": -4.0}}
    })
    assert finance_rules.margem_em_queda(ctx) is None


def test_margem_baixa_dispara_abaixo_do_minimo_configurado():
    ctx = _ctx(dashboard={"margin_pct": 22.0})
    sinal = finance_rules.margem_baixa(ctx)
    assert sinal is not None
    assert sinal.codigo == "margem_baixa"
    assert sinal.severidade is Severidade.CRITICO
    assert "22,0%" in sinal.diagnostico
    assert "25,0%" in sinal.diagnostico
    assert sinal.recomendacao is not None


def test_margem_baixa_nao_dispara_igual_ou_acima_do_minimo():
    ctx = _ctx(dashboard={"margin_pct": 25.0})
    assert finance_rules.margem_baixa(ctx) is None


def test_despesa_crescendo_dispara_com_alta_acima_do_limiar():
    ctx = _ctx(dashboard={
        "comparacao": {"month_expenses": {"atual": 2400.0, "anterior": 2000.0, "variacao_pct": 20.0}}
    })
    sinal = finance_rules.despesa_crescendo(ctx)
    assert sinal is not None
    assert sinal.codigo == "despesa_crescendo"
    assert sinal.severidade is Severidade.ATENCAO
    assert "20,0%" in sinal.diagnostico


def test_despesa_crescendo_nao_dispara_com_alta_pequena():
    ctx = _ctx(dashboard={
        "comparacao": {"month_expenses": {"atual": 2100.0, "anterior": 2000.0, "variacao_pct": 5.0}}
    })
    assert finance_rules.despesa_crescendo(ctx) is None


# ---------------------------------------------------------------------------
# stock_rules
# ---------------------------------------------------------------------------

_VARIANTE = {
    "product_name": "Manto Titã", "sku": "MT-01", "size": "M", "color": "Azul",
    "stock": 2, "margin_pct": 40.0, "sold_30d": 10,
}


def test_risco_ruptura_dispara_e_fica_critico_com_mais_de_cinco_itens():
    ctx = _ctx(produtos={"rupture_risk": [dict(_VARIANTE, days_remaining=5.0)] * 6})
    sinal = stock_rules.risco_ruptura(ctx)
    assert sinal is not None
    assert sinal.codigo == "risco_ruptura"
    assert sinal.severidade is Severidade.CRITICO
    assert "6 variantes" in sinal.diagnostico
    assert "15" in sinal.diagnostico  # rupture_days do limiar
    assert len(sinal.evidencia) == 5  # no máximo cinco, mesmo com 6 no total


def test_risco_ruptura_nao_dispara_sem_itens_em_risco():
    ctx = _ctx(produtos={"rupture_risk": []})
    assert stock_rules.risco_ruptura(ctx) is None


def test_sem_estoque_dispara_com_variantes_zeradas():
    ctx = _ctx(classificacao={"sem_estoque": [dict(_VARIANTE, stock=0)]})
    sinal = stock_rules.sem_estoque(ctx)
    assert sinal is not None
    assert sinal.codigo == "sem_estoque"
    assert sinal.severidade is Severidade.CRITICO
    assert "1 variantes" in sinal.diagnostico


def test_sem_estoque_nao_dispara_lista_vazia():
    ctx = _ctx(classificacao={"sem_estoque": []})
    assert stock_rules.sem_estoque(ctx) is None


def test_estoque_encalhado_dispara_com_produtos_parados_sem_saida():
    ctx = _ctx(classificacao={"baixa_saida_estoque_alto": [dict(_VARIANTE, sold_30d=0)]})
    sinal = stock_rules.estoque_encalhado(ctx)
    assert sinal is not None
    assert sinal.codigo == "estoque_encalhado"
    assert sinal.severidade is Severidade.ATENCAO


def test_estoque_encalhado_nao_dispara_lista_vazia():
    ctx = _ctx(classificacao={"baixa_saida_estoque_alto": []})
    assert stock_rules.estoque_encalhado(ctx) is None


def test_produto_parado_dispara_com_produtos_sem_venda_recente():
    ctx = _ctx(produtos={"stopped": [{"name": "Manto Velho", "sku": "MV-01", "total_stock": 4}]})
    sinal = stock_rules.produto_parado(ctx)
    assert sinal is not None
    assert sinal.codigo == "produto_parado"
    assert sinal.severidade is Severidade.ATENCAO
    assert "60" in sinal.diagnostico  # stopped_days do limiar


def test_produto_parado_nao_dispara_lista_vazia():
    ctx = _ctx(produtos={"stopped": []})
    assert stock_rules.produto_parado(ctx) is None


def test_estoque_critico_dispara_com_boa_saida_e_estoque_baixo():
    ctx = _ctx(classificacao={"estoque_critico": [_VARIANTE]})
    sinal = stock_rules.estoque_critico(ctx)
    assert sinal is not None
    assert sinal.codigo == "estoque_critico"
    assert sinal.severidade is Severidade.CRITICO
    assert "3" in sinal.diagnostico  # critical_stock do limiar


def test_estoque_critico_nao_dispara_lista_vazia():
    ctx = _ctx(classificacao={"estoque_critico": []})
    assert stock_rules.estoque_critico(ctx) is None


# ---------------------------------------------------------------------------
# product_rules
# ---------------------------------------------------------------------------


def test_produto_campeao_dispara_com_alta_saida_e_estoque_saudavel():
    ctx = _ctx(classificacao={"alta_saida_estoque_saudavel": [dict(_VARIANTE, stock=20)]})
    sinal = product_rules.produto_campeao(ctx)
    assert sinal is not None
    assert sinal.codigo == "produto_campeao"
    assert sinal.severidade is Severidade.BOM
    assert len(sinal.evidencia) == 1
    assert sinal.evidencia[0]["sku"] == "MT-01"


def test_produto_campeao_nao_dispara_lista_vazia():
    ctx = _ctx(classificacao={"alta_saida_estoque_saudavel": []})
    assert product_rules.produto_campeao(ctx) is None


def test_margem_alta_dispara_com_variantes_de_margem_acima_do_limiar_de_classificacao():
    ctx = _ctx(classificacao={"margem_alta": [dict(_VARIANTE, margin_pct=42.0)]})
    sinal = product_rules.margem_alta(ctx)
    assert sinal is not None
    assert sinal.codigo == "margem_alta"
    assert sinal.severidade is Severidade.BOM
    assert f"{MARGIN_HIGH:.1f}".replace(".", ",") in sinal.diagnostico


def test_margem_alta_nao_dispara_lista_vazia():
    ctx = _ctx(classificacao={"margem_alta": []})
    assert product_rules.margem_alta(ctx) is None


# ---------------------------------------------------------------------------
# channel_rules — geram um sinal por canal (lista), não um agregado
# ---------------------------------------------------------------------------


def test_canal_parou_de_vender_dispara_para_canal_que_zerou():
    ctx = _ctx(canais=[
        {
            "channel": "Instagram", "count": 0, "total": 0.0,
            "comparacao": {
                "total": {"atual": 0.0, "anterior": 1500.0, "variacao_pct": -100.0},
                "count": {"atual": 0, "anterior": 5, "variacao_pct": -100.0},
            },
        },
        {
            "channel": "Site", "count": 4, "total": 900.0,
            "comparacao": {
                "total": {"atual": 900.0, "anterior": 850.0, "variacao_pct": 5.9},
                "count": {"atual": 4, "anterior": 4, "variacao_pct": 0.0},
            },
        },
    ])
    sinais = channel_rules.canal_parou_de_vender(ctx)
    assert sinais is not None
    assert len(sinais) == 1
    assert sinais[0].codigo == "canal_parou_de_vender"
    assert sinais[0].severidade is Severidade.CRITICO
    assert "Instagram" in sinais[0].titulo
    assert "R$ 1.500,00" in sinais[0].diagnostico


def test_canal_parou_de_vender_nao_dispara_quando_nenhum_canal_zerou():
    ctx = _ctx(canais=[
        {
            "channel": "Site", "count": 4, "total": 900.0,
            "comparacao": {
                "total": {"atual": 900.0, "anterior": 850.0, "variacao_pct": 5.9},
                "count": {"atual": 4, "anterior": 4, "variacao_pct": 0.0},
            },
        },
    ])
    assert channel_rules.canal_parou_de_vender(ctx) is None


def test_canal_em_queda_dispara_para_canal_com_queda_acima_do_limiar():
    ctx = _ctx(canais=[
        {
            "channel": "Loja Física", "count": 8, "total": 800.0,
            "comparacao": {
                "total": {"atual": 800.0, "anterior": 1000.0, "variacao_pct": -20.0},
                "count": {"atual": 8, "anterior": 10, "variacao_pct": -20.0},
            },
        },
    ])
    sinais = channel_rules.canal_em_queda(ctx)
    assert sinais is not None
    assert len(sinais) == 1
    assert sinais[0].codigo == "canal_em_queda"
    assert sinais[0].severidade is Severidade.ATENCAO
    assert "Loja Física" in sinais[0].titulo
    assert "20,0%" in sinais[0].diagnostico


def test_canal_em_queda_nao_dispara_para_canal_que_ja_zerou():
    """Canal que foi a zero é o `canal_parou_de_vender` — não duplica sinal aqui."""
    ctx = _ctx(canais=[
        {
            "channel": "Instagram", "count": 0, "total": 0.0,
            "comparacao": {
                "total": {"atual": 0.0, "anterior": 1500.0, "variacao_pct": -100.0},
                "count": {"atual": 0, "anterior": 5, "variacao_pct": -100.0},
            },
        },
    ])
    assert channel_rules.canal_em_queda(ctx) is None


# ---------------------------------------------------------------------------
# data_rules
# ---------------------------------------------------------------------------


def test_qualidade_de_dados_baixa_dispara_abaixo_do_minimo():
    ctx = _ctx(qualidade={
        "score": 70.0,
        "total_issues": 3,
        "issues": {
            "no_cost_price": [{"name": "Manto X", "sku": "MX-1"}],
            "no_sale_price": [],
            "no_supplier": [],
            "no_category": [{"name": "Manto Y", "sku": "MY-1"}],
            "active_no_photo": [],
            "variants_without_info": [],
            "sales_without_channel": [],
            "expenses_without_category": [],
        },
    })
    sinal = data_rules.qualidade_de_dados_baixa(ctx)
    assert sinal is not None
    assert sinal.codigo == "qualidade_de_dados_baixa"
    assert sinal.severidade is Severidade.ATENCAO
    assert "70,0%" in sinal.diagnostico
    assert "80,0%" in sinal.diagnostico
    assert len(sinal.evidencia) == 2


def test_qualidade_de_dados_baixa_nao_dispara_acima_do_minimo():
    ctx = _ctx(qualidade={"score": 92.0, "total_issues": 0, "issues": {}})
    assert data_rules.qualidade_de_dados_baixa(ctx) is None
