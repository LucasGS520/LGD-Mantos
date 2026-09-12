"""Value object que carrega um indicador junto com seu valor no período anterior."""

from pydantic import BaseModel


class Comparado(BaseModel):
    """Um número, o mesmo número no período anterior, e a variação entre eles.

    `variacao_pct` é None sempre que a comparação não faz sentido — anterior
    ausente ou zero. Exibir "+∞%" ou "+100%" nesses casos daria ao operador uma
    falsa sensação de tendência onde não há base de comparação.
    """

    atual: float
    anterior: float | None = None
    variacao_pct: float | None = None

    @classmethod
    def de(cls, atual: float, anterior: float | None) -> "Comparado":
        """Monta o objeto já calculando a variação percentual."""
        if anterior is None or anterior == 0:
            return cls(atual=atual, anterior=anterior, variacao_pct=None)
        variacao = (atual - anterior) / anterior * 100
        return cls(atual=atual, anterior=anterior, variacao_pct=round(variacao, 1))
