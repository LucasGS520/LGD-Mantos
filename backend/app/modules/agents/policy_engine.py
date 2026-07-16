"""Policy Engine — código determinístico que bloqueia ações perigosas.

Regra: este módulo não chama LLM, não usa probabilidade, não aprende.
Cada validação é uma checagem explícita de regras de negócio.
Os agentes consultam o PolicyEngine antes de qualquer ação sensível.
"""

from dataclasses import dataclass


@dataclass
class PolicyResult:
    ok: bool
    reason: str | None = None

    @classmethod
    def allow(cls) -> "PolicyResult":
        return cls(ok=True)

    @classmethod
    def block(cls, reason: str) -> "PolicyResult":
        return cls(ok=False, reason=reason)


class PolicyEngine:
    """Conjunto de regras determinísticas que protegem a integridade operacional."""

    # ------------------------------------------------------------------
    # Validações de conteúdo
    # ------------------------------------------------------------------

    @staticmethod
    def validate_content_has_no_invented_price(text: str) -> PolicyResult:
        """Bloqueia copy que menciona preço sem contexto verificado."""
        price_patterns = ["r$", "reais", "desconto de", "% off", "promoção de"]
        lowered = text.lower()
        for pattern in price_patterns:
            if pattern in lowered:
                return PolicyResult.block(
                    f"Copy menciona preço ou desconto ('{pattern}'). "
                    "Preços devem vir dos dados operacionais, não do LLM."
                )
        return PolicyResult.allow()

    @staticmethod
    def validate_content_has_no_stock_promise(text: str) -> PolicyResult:
        """Bloqueia copy que promete disponibilidade de tamanho sem verificação."""
        stock_patterns = [
            "disponível em todos os tamanhos",
            "todos os tamanhos disponíveis",
            "estoque completo",
            "temos todos",
        ]
        lowered = text.lower()
        for pattern in stock_patterns:
            if pattern in lowered:
                return PolicyResult.block(
                    f"Copy promete disponibilidade de estoque ('{pattern}') sem verificação."
                )
        return PolicyResult.allow()

    # ------------------------------------------------------------------
    # Validações de campanha
    # ------------------------------------------------------------------

    @staticmethod
    def validate_campaign_product_has_stock(stock_quantity: int) -> PolicyResult:
        """Bloqueia campanha para produto sem estoque."""
        if stock_quantity == 0:
            return PolicyResult.block("Produto sem estoque. Não é possível criar campanha.")
        return PolicyResult.allow()

    @staticmethod
    def validate_campaign_has_no_auto_discount(campaign_data: dict) -> PolicyResult:
        """Bloqueia campanha que inclui desconto não autorizado explicitamente."""
        if campaign_data.get("discount_pct") and not campaign_data.get("discount_authorized"):
            return PolicyResult.block(
                "Campanha inclui desconto sem autorização explícita do usuário."
            )
        return PolicyResult.allow()

    # ------------------------------------------------------------------
    # Validações de aprovação
    # ------------------------------------------------------------------

    @staticmethod
    def validate_approval_is_human(approved_by: str | None) -> PolicyResult:
        """Garante que aprovação veio de um humano, nunca de um agente."""
        if not approved_by:
            return PolicyResult.block("Aprovação requer identificação do usuário humano.")
        if approved_by.lower() in ("agent", "supervisor", "auto", "system"):
            return PolicyResult.block(
                f"Aprovação não pode ser feita por '{approved_by}'. "
                "Somente usuários humanos podem aprovar conteúdo."
            )
        return PolicyResult.allow()

    # ------------------------------------------------------------------
    # Validações de publicação (para uso futuro do PublishingAgent)
    # ------------------------------------------------------------------

    @staticmethod
    def validate_publish_requires_approval(approval_status: str) -> PolicyResult:
        """Bloqueia publicação sem aprovação humana."""
        if approval_status != "approved":
            return PolicyResult.block(
                f"Publicação bloqueada: status de aprovação é '{approval_status}', "
                "requer 'approved'."
            )
        return PolicyResult.allow()

    @staticmethod
    def validate_publish_channel_is_authorized(channel: str, authorized_channels: list[str]) -> PolicyResult:
        """Bloqueia publicação em canal não autorizado."""
        if channel not in authorized_channels:
            return PolicyResult.block(
                f"Canal '{channel}' não está na lista de canais autorizados: "
                f"{authorized_channels}."
            )
        return PolicyResult.allow()

    # ------------------------------------------------------------------
    # Operações proibidas — barreiras absolutas
    # ------------------------------------------------------------------

    @staticmethod
    def block_stock_mutation() -> PolicyResult:
        """Agentes nunca podem alterar estoque."""
        return PolicyResult.block("Agentes não têm permissão para alterar estoque.")

    @staticmethod
    def block_price_mutation() -> PolicyResult:
        """Agentes nunca podem alterar preço."""
        return PolicyResult.block("Agentes não têm permissão para alterar preços.")

    @staticmethod
    def block_sale_registration() -> PolicyResult:
        """Agentes nunca podem registrar vendas."""
        return PolicyResult.block("Agentes não têm permissão para registrar vendas.")

    @staticmethod
    def block_product_deletion() -> PolicyResult:
        """Agentes nunca podem apagar produtos."""
        return PolicyResult.block("Agentes não têm permissão para apagar produtos.")

    @staticmethod
    def block_local_image_generation() -> PolicyResult:
        """Agentes não geram imagens localmente no MVP."""
        return PolicyResult.block("Geração local de imagem não está disponível no MVP.")

    @staticmethod
    def block_auto_publish() -> PolicyResult:
        """Publicação automática bloqueada no MVP."""
        return PolicyResult.block("Publicação automática não está disponível no MVP.")
