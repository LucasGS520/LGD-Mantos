from typing import Literal

from ..common.schemas import AuxiliaryFields


class SuppliersIn(AuxiliaryFields):
    kind: Literal["supplier"] = "supplier"
