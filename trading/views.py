from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from decimal import Decimal, InvalidOperation
import json 
from stocks.models import Stock, PriceBar
from . models import Portfolio, execute_market_order, Trade, Position, PendingOrder


@login_required
@require_POST
def place_market_order(request):
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '').upper().strip()
        trade_type = data.get('trade_type', '').upper().strip()
        raw_quantity = data.get('quantity', 0)

        if trade_type not in ('BUY', 'SELL'):
            return JsonResponse({"success":False, 'error':'Invalid trade type'}, status=400)
        
        try:
            quantity = Decimal(str(raw_quantity))
        except InvalidOperation:
            return JsonResponse({'success':False, 'error':'Invalid quantity'}, status=400)
        
        if quantity <= 0:
            return JsonResponse({'success':False, 'error':'Quantity must be greater than 0'}, status=400)
        
        
        stock = Stock.objects.get(symbol = symbol)
        portfolio = request.user.portfolio

        trade = execute_market_order(portfolio, stock, trade_type, quantity)

        portfolio.refresh_from_db()

        return JsonResponse({
            'success':True,
            'message':f'{trade_type} {quantity} {symbol} @ {trade.price}',
            'new_cash':str(portfolio.cash),
            'trade_price':str(trade.price),
            'total_value':str(trade.total_value),
        })
        
    except Stock.DoesNotExist:
        return JsonResponse({'success':False, 'error':f'Stock not found'}, status=400)
    except ValueError as e:
        return JsonResponse({'success':False, 'error':str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success':False, 'error':'Something went wrong'}, status=500)
    

@login_required
def portfolio_dashboard(request):
    portfolio = request.user.portfolio
    positions = portfolio.positions.filter(quantity__gt=0).select_related('stock')

    enriched_positions = []
    total_holdings_value = Decimal('0')

    for pos in positions:
        latest = PriceBar.objects.filter(stock=pos.stock).order_by('-timestamp').first()

        if latest:
            current_price = latest.close
        else:
            current_price = pos.avg_cost
        
        current_value = current_price * pos.quantity
        cost_basis = pos.avg_cost * pos.quantity
        pnl = current_value - cost_basis
        pnl_pct = (pnl / cost_basis * 100) if  cost_basis > 0 else Decimal('0')

        total_holdings_value += current_value

        enriched_positions.append({
            'stock':pos.stock,
            'quantity':pos.quantity,
            'avg_cost':pos.avg_cost,
            'current_price':current_price,
            'current_value':current_value,
            'pnl':pnl,
            'pnl_pct':pnl_pct,
        })
    
    total_portfolio_value = portfolio.cash + total_holdings_value
    total_pnl = total_portfolio_value - Decimal('100000')

    pending_orders = PendingOrder.objects.filter(
        portfolio=portfolio, 
        status='PENDING'
        ).select_related('stock').order_by('-created_at')
    

    recent_trades = portfolio.trades.select_related('stock').order_by('-executed_at')[:10]

    return render(request, 'trading/dashboard.html', {
        'portfolio':portfolio,
        'positions':enriched_positions,
        'pending_orders':pending_orders,
        'recent_trades':recent_trades,
        'total_portfolio_value':total_portfolio_value,
        'total_holdings_value':total_holdings_value,
        'total_pnl':total_pnl
    })

@login_required
@require_POST
def place_limit_order(request):
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '').upper().strip()
        order_type = data.get('order_type', '').upper().strip()
        raw_quantity = data.get('quantity', 0)
        raw_trigger_price = data.get('trigger_price', 0)

        valid_types = ('LIMIT_BUY', 'LIMIT_SELL', 'STOP_LOSS', 'TAKE_PROFIT')
        if order_type not in valid_types:
            return JsonResponse({'success':False, 'error':'Invalid order type'}, status=400)
        
        try:
            quantity = Decimal(str(raw_quantity))
            trigger_price = Decimal(str(raw_trigger_price))

        except InvalidOperation:
            return JsonResponse({'success':False, 'error':'Invalid quantity or price'}, status=400)
        
        if quantity <= 0 or trigger_price <= 0:
            return JsonResponse({'success':False, 'error':'Quantity and price must be greater than 0'}, status=400)
        
        stock = Stock.objects.get(symbol=symbol)
        portfolio = request.user.portfolio

        order = PendingOrder.objects.create(
            portfolio=portfolio,
            stock=stock,
            order_type=order_type,
            quantity=quantity,
            trigger_price=trigger_price,
        )
        return JsonResponse({
            'success':True,
            'message':f"{order_type} order placed - {quantity} {symbol} @ {trigger_price}",
            'order_id':order.id,
        })
    except Stock.DoesNotExist:
        return JsonResponse({'success':False, 'error':'Stock not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success':False, 'error':'Something went wrong'}, status=500)
    

@login_required
@require_POST
def cancel_limit_order(request, order_id):
    try:
        order = PendingOrder.objects.get(
            id=order_id,
            portfolio=request.user.portfolio,
            status='PENDING'
        )
        order.status = 'CANCELLED'
        order.save()
        return JsonResponse({'success':True, 'message':'Order cancelled'})
    except PendingOrder.DoesNotExist:
        return JsonResponse({'success':False, 'error':'Order not found'}, status=404)
    

@login_required
@require_POST
def place_stop_order(request):
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '').upper().strip()
        order_type = data.get('order_type', '').upper().strip()
        raw_quantity = data.get('quantity',0)
        raw_trigger_price = data.get('trigger_price', 0)

        if order_type not in ('STOP_LOSS', 'TAKE_PROFIT'):
            return JsonResponse({'success':False, 'error':'Invalid order type'}, status=400)
        
        try:
            quantity = Decimal(str(raw_quantity))
            trigger_price = Decimal(str(raw_quantity))
        except InvalidOperation:
            return JsonResponse({'success':False,'error':'Invalid quantity or price'},status=400)
        
        if quantity <=0 or trigger_price <= 0:
            return JsonResponse({'success':False, 'error':'Quantity and price must be greater than 0'},status=400)
        
        stock = Stock.objects.get(symbol=symbol)
        portfolio = request.user.portfolio

        latest = PriceBar.objects.filter(stock=stock).order_by('-timestamp').first()
        if not latest:
            return JsonResponse({"success":False, "message":"No price data available"}, status=400)
        
        current_price = latest.close
        if order_type == 'STOP_LOSS' and trigger_price >= current_price:
            return JsonResponse({
                'success':False,
                'error':f'stop-loss price {trigger_price} must be below current price {current_price}'
            }, status=400)
        
        if order_type == 'TAKE_PROFIT' and trigger_price <= current_price:
            return JsonResponse({
                'success':False,
                'error':f'take-profit price {trigger_price}, must be above current price {current_price}'
            }, status=400)
        
        try:
            position = Position.objects.get(portfolio=portfolio, stock=stock)
            if position.quantity < quantity:
                return JsonResponse({
                    'success':False,
                    'error':f"You only have {position.quantity} shares, cannot set order for {quantity}"
                }, status=400)
        
        except Position.DoesNotExist:
            return JsonResponse({
                'success':False,
                'message':f"You do not hold any {symbol} shares"
            }, status=400)
            
        order = PendingOrder.objects.create(
            portfolio=portfolio,
            stock=stock,
            order_type=order_type,
            quantity=quantity,
            trigger_price=trigger_price,
        )
        return JsonResponse({
            'success':True,
            'message':f"{order_type} set for {quantity} {symbol} @ {trigger_price}",
            'order_id':order.id
        })
        
    except Stock.DoesNotExist:
            return JsonResponse({'success':False, 'error':'Stock not found'}, status=400)
    except Exception as e:
            return JsonResponse({'success':False, 'error':'Something went wrong'}, status=500)
        