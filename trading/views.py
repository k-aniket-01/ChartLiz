from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from decimal import Decimal, InvalidOperation
import json 
from stocks.models import Stock
from . models import Portfolio, execute_market_order, Trade, Position


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
    position = portfolio.positions.filter(quantity__gt=0).select_related('stock')
    recent_trades = portfolio.trades.order_by('-executed_at')[:10]

    return render(request, 'trading/dashboard.html', {
        'portfolio':portfolio,
        'position':position,
        'recent_trades':recent_trades,
    })