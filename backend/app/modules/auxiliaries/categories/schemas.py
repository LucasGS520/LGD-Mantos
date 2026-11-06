from typing import Literal

from ..common.schemas import AuxiliaryFields


class CategoriesIn(AuxiliaryFields):
    kind: Literal["category"] = "category"
