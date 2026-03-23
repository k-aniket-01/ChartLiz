from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction as db_transaction


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

class Trade(models.Model):
    TRADE_TYPES = [('BUY', 'Buy'),('SELL','Sell')]
    stock = models.ForeignKey('stocks.Stock', on_delete=models.CASCADE) 
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='trades')
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    price = models.DecimalField(max_digits=10, decimal_places=4)
    executed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.trade_type} {self.quantity} {self.stock.symbol} @ {self.price}"
    
    @property
    def total_value(self):
        return self.quantity * self.price
    
def execute_market_order(portfolio, stock, trade_type, quantity):
    from decimal import Decimal
    from stocks.models import PriceBar

    latest_bar = PriceBar.objects.filter(stock=stock).order_by('-timestamp').first()
    if not latest_bar:
        raise ValueError(f"No price data available for {stock.symbol}")
    
    price = latest_bar.close
    total_cost = price * Decimal(str(quantity))

    with db_transaction.atomic():
        portfolio = Portfolio.objects.select_for_update().get(pk=portfolio.pk)
        position, _ = Position.objects.get_or_create(portfolio=portfolio, stock=stock)

        if trade_type == 'BUY':
            if portfolio.cash < total_cost:
                raise ValueError(f"Insufficient funds. Need {total_cost:.2f}, have {portfolio.cash:.2f}")
            
            if position.quantity > 0:
                position.avg_cost = (
                    (position.avg_cost * position.quantity) + (price * Decimal(str(quantity)))
                ) / (position.quantity + Decimal(str(quantity)))
            else:
                position.avg_cost = price

            position.quantity += Decimal(str(quantity))
            portfolio.cash -= total_cost

        elif trade_type == 'SELL':
            if position.quantity < Decimal(str(quantity)):
                raise ValueError(
                    f"Insufficient shares. Want to sell {quantity}, only have {position.quantity}"
                )
            
            position.quantity -= Decimal(str(quantity))
            portfolio.cash += total_cost

            if position.quantity == 0:
                position.avg_cost = Decimal('0')
        
        position.save()
        portfolio.save()

        trade = Trade.objects.create(
            portfolio = portfolio,
            stock = stock,
            trade_type = trade_type,
            quantity = Decimal(str(quantity)),
            price = price
        )
    return trade

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_portfolio(sender, instance, created, **kwargs):
    if created:
        Portfolio.objects.create(user = instance)


class PendingOrder(models.Model):
    ORDER_TYPES = [
        ('LIMIT_BUY', 'Limit Buy'),
        ('LIMIT_SELL', 'Limit Sell'),
        ('STOP_LOSS', 'Stop Loss'),
        ('TAKE_PROFIT', 'Take Profit'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('FILLED', 'Filled'),
        ('CANCELLED', 'Cancelled'),
    ]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='pending_orders')
    stock = models.ForeignKey('stocks.Stock', on_delete=models.CASCADE)
    order_type = models.CharField(max_length=12, choices=ORDER_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    trigger_price = models.DecimalField(max_digits=10, decimal_places=4)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    filled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.order_type} {self.quantity} @{self.trigger_price} {self.status}"
    

