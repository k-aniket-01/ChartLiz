from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Stock, PriceBar, Watchlist
from django.db.models import Q
from datetime import datetime
import pytz
import yfinance as yf
import pandas as pd 

@login_required
def stock_detail(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol.upper())
    in_watchlist = Watchlist.objects.filter(user=request.user, stock=stock).exists()
    return render(request, 'stocks/stock_detail.html', {'stock':stock, 'in_watchlist':in_watchlist})


@login_required
def ohlcv_api(request, symbol):
    timeframe = request.GET.get('timeframe','1d')
    bars = PriceBar.objects.filter(
        stock__symbol= symbol.upper(),
        timeframe = timeframe
    ).values('timestamp','open','high','low','close','volume')

    data= []
    for bar in bars:
        data.append({
            'timestamp':str(bar['timestamp']),
            'open':float(bar['open']),
            'high':float(bar['high']),
            'low':float(bar['low']),
            'close':float(bar['close']),
            'volume':bar['volume'],
        })
    return JsonResponse({'symbol':symbol.upper(), 'data':data})


@login_required
def stock_search(request):
    return render(request, 'stocks/search.html')


@login_required
def stock_search_api(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 1:
        return JsonResponse({'results': []})
    
    stocks = Stock.objects.filter(
        Q(symbol__icontains=query) | Q(name__icontains=query)
    )[:10]

    results = [
        {'symbol': s.symbol, 'name':s.name, 'exchange':s.exchange}for s in stocks
    ]
    return JsonResponse({'results':results})


# stocks/views.py — replace the watchlist view

@login_required
def watchlist(request):
    items = Watchlist.objects.filter(user=request.user).select_related('stock')

    # Portfolio summary
    from trading.models import Portfolio, Position
    from alerts.models import Notification
    from patterns.models import PatternDetection

    try:
        portfolio = Portfolio.objects.get(user=request.user)
        positions = Position.objects.filter(
            portfolio=portfolio, quantity__gt=0
        ).select_related('stock')
    except Exception:
        portfolio = None
        positions = []

    # Last 5 notifications
    recent_notifications = Notification.objects.filter(
        user=request.user
    )[:5]

    # Recent pattern detections across watchlist stocks
    watchlist_symbols = [i.stock.symbol for i in items]
    recent_patterns = PatternDetection.objects.filter(
        stock__symbol__in=watchlist_symbols
    ).select_related('stock').order_by('-detected_at')[:8]

    return render(request, 'stocks/watchlist.html', {
        'items':                items,
        'portfolio':            portfolio,
        'positions':            positions,
        'recent_notifications': recent_notifications,
        'recent_patterns':      recent_patterns,
    })

@login_required
def toggle_watchlist(request, symbol):
    if request.method == 'POST':
        stock = get_object_or_404(Stock, symbol=symbol.upper())
        item, created = Watchlist.objects.get_or_create(user= request.user, stock=stock)
        if not created:
            item.delete()
            in_watchlist = False
        else:
            in_watchlist= True
        return JsonResponse({'in_watchlist':in_watchlist})
    

@login_required
def market_status(request):
    now_et = datetime.now(pytz.timezone('America/New_York'))
    weekday = now_et.weekday()
    hour = now_et.hour
    minute = now_et.minute
    current_time =  hour * 100 + minute
    is_open = (
        weekday < 5 and
        930 <= current_time <= 1600
    )
    return JsonResponse({
        "is_open":is_open,
        'time_et':now_et.strftime('%I:%M %p ET'),
        'day':now_et.strftime('%A'),
    })


def stock_ohlcv(request, symbol):
    period = request.GET.get('period', '3mo')
    interval = request.GET.get('interval', '1d')

    ticker = yf.Ticker(symbol.upper())
    df = ticker.history(period=period, interval=interval)

    df.index = df.index.tz_localize(None) if df.index.tz is not None else df.index

    df['sma20'] = df['Close'].rolling(window=20).mean()
    df['sma50'] = df['Close'].rolling(window=50).mean()
    df['sma200'] = df['Close'].rolling(window=200).mean()
    df['rsi'] = calculate_rsi(df['Close'])
    df['macd'], df['macd_signal'], df['macd_hist'] = calculate_macd(df['Close'])
    df['bb_mid'] = df['Close'].rolling(window=20).mean()
    df['bb_upper'] = df['bb_mid'] + 2 * df['Close'].rolling(window=20).std()
    df['bb_lower'] = df['bb_mid'] - 2 * df['Close'].rolling(window=20).std()

    intraday = interval in ['1m','5m','15m','30m','60m','90m']

    data = []
    for dt, row in df.iterrows():
        time_val = int(dt.timestamp()) if intraday else dt.strftime('%Y-%m-%d')
        candle = {
            'time':time_val,
            'open':round(row['Open'],2),
            'high':round(row['High'],2),
            'low':round(row['Low'],2),
            'close':round(row['Close'],2),   
            'volume': int(row['Volume']),   
            }
        if pd.notna(row['sma20']):
            candle['sma20'] = round(row['sma20'], 2)
        if pd.notna(row['sma50']):  
            candle['sma50'] = round(row['sma50'], 2)
        if pd.notna(row['sma200']):
            candle['sma200'] = round(row['sma200'], 2)
        if pd.notna(row['rsi']):
            candle['rsi'] = round(row['rsi'], 2)
        if pd.notna(row['macd']):
            candle['macd'] = round(row['macd'], 4)
            candle['macd_signal'] = round(row['macd_signal'], 4)
            candle['macd_hist'] = round(row['macd_hist'], 4)
        if pd.notna(row['bb_upper']):
            candle['bb_upper'] = round(row['bb_upper'], 2)
            candle['bb_mid'] = round(row['bb_mid'], 2)
            candle['bb_lower'] = round(row['bb_lower'], 2)
        data.append(candle)

    return JsonResponse(data, safe=False)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = (-delta).clip(lower=0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram