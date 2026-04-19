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

fake = Faker()


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = Role
        django_get_or_create = ('name',)  # Don't create duplicates

    name = Role.STORE_MANAGER


class LocationFactory(DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.LazyFunction(lambda: f"{fake.city()} Store")
    type = Location.LocationType.STORE
    is_active = True


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyFunction(lambda: fake.unique.email())
    name = factory.LazyFunction(lambda: fake.name())
    role = factory.SubFactory(RoleFactory)
    location = factory.SubFactory(LocationFactory)
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Use create_user so password gets hashed correctly."""
        return model_class.objects.create_user(*args, **kwargs)


class AdminUserFactory(UserFactory):
    role = factory.SubFactory(RoleFactory, name=Role.ADMIN)


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.LazyFunction(lambda: fake.unique.word().capitalize())


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.LazyFunction(lambda: fake.unique.word().capitalize())
    sku = factory.LazyFunction(lambda: f"SKU-{fake.unique.numerify('####')}")
    category = factory.SubFactory(CategoryFactory)
    unit_of_measure = Product.UnitOfMeasure.PIECE
    unit_price_cost = Decimal('1.00')
    unit_price_retail = Decimal('1.50')
    tax_rate = Decimal('0.00')
    is_active = True


class SupplierFactory(DjangoModelFactory):
    class Meta:
        model = Supplier

    name = factory.LazyFunction(lambda: fake.company())
    is_active = True


class StockLevelFactory(DjangoModelFactory):
    class Meta:
        model = StockLevel

    product = factory.SubFactory(ProductFactory)
    location = factory.SubFactory(LocationFactory)
    quantity_on_hand = Decimal('100.00')
    quantity_reserved = Decimal('0.00')
    reorder_point = Decimal('20.00')
    reorder_quantity = Decimal('50.00')


class PurchaseOrderFactory(DjangoModelFactory):
    class Meta:
        model = PurchaseOrder

    supplier = factory.SubFactory(SupplierFactory)
    destination_location = factory.SubFactory(LocationFactory)
    status = PurchaseOrder.Status.CONFIRMED


class StockTransferFactory(DjangoModelFactory):
    class Meta:
        model = StockTransfer

    from_location = factory.SubFactory(LocationFactory)
    to_location = factory.SubFactory(LocationFactory)
    status = StockTransfer.Status.APPROVED
    requested_by = factory.SubFactory(UserFactory)