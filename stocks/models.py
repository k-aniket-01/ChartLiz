from django.db import models
from users.models import User
# Create your models here.

class Stock(models.Model):
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    exchange = models.CharField(max_length=60, blank=True)
    sector = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} - {self.symbol}"


class PriceBar(models.Model):
    timeframe_choices = [
        ('1m', '1 Minute'),
        ('5m', '5 Minutes'),
        ('1h', '1 Hour'),
        ('1d', '1 Day'),
    ]
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='price_bars')
    timeframe = models.CharField(max_length=6, choices=timeframe_choices)
    timestamp = models.DateField()
    open = models.DecimalField(max_digits=12, decimal_places=4)
    high = models.DecimalField(max_digits=12, decimal_places=4)
    low = models.DecimalField(max_digits=12, decimal_places=4)
    close = models.DecimalField(max_digits=12, decimal_places=4)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('stock', 'timeframe', 'timestamp')
        indexes = [models.Index(fields = ['stock', 'timeframe', 'timestamp']),]
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.stock.symbol} {self.timeframe} @ {self.timestamp}"
    

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'stock')
        
    def __str__(self):
        return f"{self.user.username} watching {self.stock.symbol}"
    