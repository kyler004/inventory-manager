from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.products.views import ProductViewSet, CategoryViewSet
from apps.stock.views import (
    StockLevelViewSet, StockAdjustmentViewSet, StockMovementViewSet
)

# The Router automatically generates all standard urls
# for each viewset - list, detail, create, update, delete

router = DefaultRouter()

#Product
router.register(r'products', ProductViewSet, basename='product')
router.register(r'products/categories', CategoryViewSet, basename='category')

#Stock
router.register(r'stock', StockLevelViewSet, basename="stock")
router.register(r'stock/adjustments', StockAdjustmentViewSet, basename="stock-adjustment")
router.register(r'stock/movements', StockMovementViewSet, basename='stock-movement')

urlpatterns = [
    path('', include(router.urls)), 
    path('auth/', include('apps.authentication.urls')),
]