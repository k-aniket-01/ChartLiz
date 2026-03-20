from django.contrib import admin
from .models import Portfolio, Position

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'cash', 'is_active', 'created_at')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'stock', 'quantity', 'avg_cost')