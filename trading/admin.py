from django.contrib import admin
from .models import Portfolio, Position, Trade

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'cash', 'is_active', 'created_at')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'stock', 'quantity', 'avg_cost')

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'stock', 'trade_type', 'quantity', 'price', 'executed_at')