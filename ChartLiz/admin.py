from django.contrib import admin
from .models import Buy, Trade, Portfolio, Transaction, Sell

# Register your models here
admin.site.register(Buy)
admin.site.register(Trade)
admin.site.register(Portfolio)
admin.site.register(Transaction)
admin.site.register(Sell)
