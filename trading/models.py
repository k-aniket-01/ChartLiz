from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_portfolio(sender, instance, created, **kwargs):
    if created:
        Portfolio.objects.create(user = instance)

class Portfolio(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cash = models.DecimalField(max_digits=12, decimal_places=2, default=100000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s portfolio ({self.cash})"

    # @property
    # def total_value(self):
    #     holding_value = sum(p.current_value for p in self.positions.filter(quantity__gt=0))
    #     return self.cash + holding_value


class Position(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='positions')
    stock = models.ForeignKey('stocks.Stock', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    avg_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    class Meta:
        unique_together = ('portfolio','stock')
    
    def __str__(self):
        return f"{self.portfolio.user.username} - {self.stock.symbol} X{self.quantity}"

    # @property
    # def current_value(self):
    #     latest = self.stock.pricebars.order_by('datetime').first()
    #     return (latest.close * self.quantity) if latest else 0 
    
    # @property
    # def unrealized_pnl(self):
    #     return self.current_value - (self.avg_cost * self.quantity)