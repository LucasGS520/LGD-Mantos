"""Registro dos quinze modelos; sem abrir conexão ou carregar segredos."""

from .auxiliaries import AUXILIARY_MODELS as AUXILIARY_MODELS
from .auxiliaries import Category as Category
from .auxiliaries import PaymentMethod as PaymentMethod
from .auxiliaries import PurchaseChannel as PurchaseChannel
from .auxiliaries import SaleChannel as SaleChannel
from .auxiliaries import Supplier as Supplier
from .catalog import Photo as Photo
from .catalog import Product as Product
from .catalog import Variant as Variant
from .history import Control as Control
from .history import Movement as Movement
from .history import RequestReceipt as RequestReceipt
from .history import Revision as Revision
from .metadata import Base as Base
from .operations import Operation as Operation
from .operations import OperationItem as OperationItem
from .operations import SalePayment as SalePayment
