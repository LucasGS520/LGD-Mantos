from typing import Annotated, Union

from pydantic import Field

from .categories.schemas import CategoriesIn
from .payment_methods.schemas import PaymentMethodsIn
from .purchase_channels.schemas import PurchaseChannelsIn
from .sale_channels.schemas import SaleChannelsIn
from .suppliers.schemas import SuppliersIn

AuxiliaryIn = Annotated[
    Union[SuppliersIn, CategoriesIn, PurchaseChannelsIn, SaleChannelsIn, PaymentMethodsIn],
    Field(discriminator="kind"),
]
