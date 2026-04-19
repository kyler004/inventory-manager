from django.contrib import admin
from .models import StockLevel, StockMovement, StockAdjustment

admin.site.register(StockLevel)
admin.site.register(StockMovement)
admin.site.register(StockAdjustment)
