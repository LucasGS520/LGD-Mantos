from typing import Literal

from ..common.schemas import AuxiliaryFields


class SaleChannelsIn(AuxiliaryFields):
    kind: Literal["sale_channel"] = "sale_channel"
