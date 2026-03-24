import logging
from celery import shared_task
from django.utils import timezone
import yfinance as yf
from .models import Stock, PriceBar

logger = logging.getLogger(__name__)

@shared_task
def fetch_stock_data(symbol, timeframe='1d'):
    try:
        config = {
            '1m': {'interval': '1m', 'period': '1d'},
            '5m': {'interval': '5m', 'period': '5d'},
            '1h': {'interval': '1h', 'period': '1mo'},
            '1d': {'interval': '1d', 'period': '1y'},
        }

        if timeframe not in config:
            logger.error(f'Invalid timeframe: {timeframe}')
            return
        
        cfg = config[timeframe]
        ticker = yf.Ticker(symbol)
        info = ticker.info

        stock, created = Stock.objects.get_or_create(
            symbol = symbol.upper(),
            defaults={
                'name':info.get('longName', symbol),
                'exchange':info.get('exchange', ''),
                'sector': info.get('sector', '')
            }
        )
        
        df = ticker.history(
            interval=cfg['interval'],
            period=cfg['period']
        )

        if df.empty:
            logger.warning(f'No data returned for {symbol}')
            return
        saved = 0 
        
        for timestamp, row in df.iterrows():
            if timestamp.tzinfo is None:
                timestamp = timezone.make_aware(timestamp)
            obj, created = PriceBar.objects.update_or_create(
                stock=stock,
                timeframe=timeframe,
                timestamp=timestamp,
                defaults={
                    'open': round(float(row['Open']), 4),
                    'high': round(float(row['High']), 4),
                    'low': round(float(row['Low']), 4),
                    'close': round(float(row['Close']), 4),
                    'volume': int(row['Volume']),
                }
            )
            if created:
                saved +=1
        logger.info(f'Fetched {symbol} {timestamp}: {saved} new candle saved')

        # ← ADD THE BROADCAST CODE HERE
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        latest = PriceBar.objects.filter(
            stock=stock,
            timeframe=timeframe
        ).last()

        if latest:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'stock_{symbol.upper()}',
                {
                    'type': 'stock_price_update',
                    'data': {
                        'symbol': symbol.upper(),
                        'open': float(latest.open),
                        'high': float(latest.high),
                        'low': float(latest.low),
                        'close': float(latest.close),
                        'volume': latest.volume,
                        'timestamp': str(latest.timestamp),
                    }
                }
            )
            if timeframe in ('1m', '1d'):
                from trading.tasks import check_pending_orders
                check_pending_orders.__delay(symbol.upper(), float(latest.close))
        return f'{saved} candle saved for {symbol}'
    
    except Exception as e:
        logger.error(f'Error fetching {symbol}: {e}')
        raise


@shared_task
def fetch_all_watchlist_stocks():
    symbols = Stock.objects.filter(ia_active=True).values_list('symbol',flat=True)
    for symbol in symbols:
        fetch_stock_data.delay(symbol, '1d')
        fetch_stock_data.delay(symbol, '1h')
        