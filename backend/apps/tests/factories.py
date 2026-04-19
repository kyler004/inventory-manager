import factory
from factory.django import DjangoModelFactory
from faker import Faker
from decimal import Decimal

from apps.users.models import User, Role
from apps.locations.models import Location, Zone
from apps.products.models import Category, Product
from apps.suppliers.models import Supplier, SupplierProduct
from apps.stock.models import StockLevel
from apps.purchase_orders.models import PurchaseOrder, PurchaseOrderItem
from apps.transfers.models import StockTransfer, StockTransferItem
from apps.batches.models import Batch

