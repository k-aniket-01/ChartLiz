from celery import shared_task
from decimal import Decimal
from django.utils import timezone
from stocks.models import Stock
from .models import PendingOrder, execute_market_order

@shared_task
def check_pending_orders(stock_symbol, current_price):
    try:
        current_price = Decimal(str(current_price))
        stock = Stock.objects.get(symbol=stock_symbol)

        pending_orders = PendingOrder.objects.filter(
            stock=stock,
            status='PENDING',    
            ).select_related('portfolio', 'stock')
        
        for order in pending_orders:
            should_fill = False
            trade_type = None

            if order.order_type == 'LIMIT_BUY' and current_price <= order.trigger_price:
                should_fill = True
                trade_type = 'BUY'

            if order.order_type == 'LIMIT_SELL' and current_price <= order.trigger_price:
                should_fill = True
                trade_type = 'SELL'

            if order.order_type == 'STOP_LOSS' and current_price <= order.trigger_price:
                should_fill = True
                trade_type = 'SELL'

            if order.order_type == 'TAKE_PROFIT' and current_price <= order.trigger_price:
                should_fill = True
                trade_type = 'SELL'
            
            if should_fill:
                try:
                    execute_market_order(
                        order.portfolio,
                        order.stock,
                        trade_type,
                        order.quantity
                    )
                    order.status = 'FILLED'
                    order.filled_at = timezone.now()
                    order.save()
                    print(f"Filled {order.order_type} for {order.stock.symbol}")
                except ValueError as e:
                    print(f"Could not fill order {order.id}: {e}")
    
    except Stock.DoesNotExist:
        print(f"Stock {stock_symbol} not found")