from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Transaction(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_balance = models.FloatField(default=200000.0)  # Initial $200,000

    def __str__(self):
        return f"{self.user.username}'s Wallet - ${self.wallet_balance}"

class Trade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin_name = models.CharField(max_length=100, default='bitcoin')  # <-- Added default
    coin_symbol = models.CharField(max_length=20, default='BTCUSDT')
    action = models.CharField(max_length=10, default='buy')  # buy or sell
    price = models.FloatField()
    quantity = models.FloatField(default=0)  # <-- Add this line
    timestamp = models.DateTimeField(auto_now_add=True)
 

class Buy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin_name = models.CharField(max_length=50)
    coin_symbol = models.CharField(max_length=20, default='') 
    price = models.FloatField()
    quantity = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


from django.db import models
from django.contrib.auth.models import User

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin_name = models.CharField(max_length=100, null=True, blank=True)
    coin_symbol = models.CharField(max_length=20, default='') 
    quantity = models.FloatField(default=0)
    buy_price = models.FloatField(default=0)       # Per unit
    current_price = models.FloatField(default=0)   # Per unit

    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def total_value(self):
        return round(self.quantity * self.current_price, 2)

    @property
    def invested_value(self):
        return round(self.quantity * self.buy_price, 2)

    @property
    def profit_loss_amount(self):
        return round(self.total_value - self.invested_value, 2)

    @property
    def profit_loss_percent(self):
        try:
            return round((self.profit_loss_amount / self.invested_value) * 100, 2)
        except ZeroDivisionError:
            return 0.0

    def __str__(self):
        return f"{self.user.username} - {self.coin_symbol}"




class Sell(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin_name = models.CharField(max_length=100)
    coin_symbol = models.CharField(max_length=20)
    quantity = models.FloatField()
    sell_price = models.FloatField()  # Per unit at time of sale
    total_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Sold {self.quantity} {self.coin_symbol} at ${self.sell_price}"
