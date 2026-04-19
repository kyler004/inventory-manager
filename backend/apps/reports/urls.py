from django.urls import path
from .views import (
    StockValuationView, ShrinkageView, 
    TurnoverView, DeadStockView, SupplierPerformanceView
)

urlpatterns = [
    path('stock-valuation/', StockValuationView.as_view()),
    path('shrinkage/', ShrinkageView.as_view()),
    path('turnover/', TurnoverView.as_view()),
    path('dead-stock/', DeadStockView.as_view()),
    path('supplier-performance/', SupplierPerformanceView.as_view()),
]