"""Schemas Pydantic das preferências de alerta configuráveis do sistema."""

from datetime import datetime

from pydantic import BaseModel, Field


class PreferencesOut(BaseModel):
    """Limiares de alerta atualmente em vigor (padrão quando ainda não configurados)."""

    rupture_days: int
    stopped_days: int
    critical_stock: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class PreferencesUpdate(BaseModel):
    """Payload para atualizar os limiares de alerta.

    Os intervalos refletem limites de negócio razoáveis — evitam configurações
    absurdas (ex.: ruptura em 0 dias) sem travar casos de uso legítimos.
    """

    rupture_days: int = Field(
        ge=1, le=90,
        description="Dias de cobertura de estoque abaixo dos quais a variante entra em risco de ruptura",
    )
    stopped_days: int = Field(
        ge=7, le=365,
        description="Dias sem venda para o produto ser considerado parado",
    )
    critical_stock: int = Field(
        ge=0, le=100,
        description="Estoque igual ou abaixo do qual soa alerta de reposição antes de postar",
    )
