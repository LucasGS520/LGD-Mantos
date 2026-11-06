from typing import Literal

from ..common.schemas import AuxiliaryFields


class PaymentMethodsIn(AuxiliaryFields):
    kind: Literal["payment_method"] = "payment_method"
