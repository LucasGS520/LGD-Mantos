from typing import Literal

from ..common.schemas import AuxiliaryFields


class PurchaseChannelsIn(AuxiliaryFields):
    kind: Literal["purchase_channel"] = "purchase_channel"
