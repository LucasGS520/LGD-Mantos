"""Formatação de números para os textos de `diagnostico`/`recomendacao`.

Compartilhado por todos os módulos de regra — evita reimplementar a mesma
conversão de separador decimal em cada arquivo. Não depende de `locale` do
sistema operacional (frágil entre ambientes/containers): faz a troca de
separadores na mão.
"""


def formatar_moeda(valor: float) -> str:
    """Formata um valor em reais no padrão BR: milhar com ponto, decimal com vírgula.

    Ex.: 1234.5 -> "R$ 1.234,50".
    """

    # Trunque em duas casas primeiro (formatação americana), depois troca os
    # separadores. O placeholder "@" evita colisão entre as duas trocas.
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "@").replace(".", ",").replace("@", ".")
    return f"R$ {texto}"


def formatar_pct(valor: float) -> str:
    """Formata um percentual com uma casa decimal, vírgula como separador.

    Ex.: 15.0 -> "15,0". O caractere "%" não entra aqui — cada regra decide
    onde ele fica na frase (às vezes junto do número, às vezes não).
    """

    return f"{valor:.1f}".replace(".", ",")
