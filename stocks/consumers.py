import json 
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Stock, PriceBar
from django.utils import timezone
from datetime import date

class StockPriceConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.symbol = self.scope['url_route']['kwargs']['symbol'].upper()
        self.group_name = f'stock_{self.symbol}'
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        latest = await self.get_latest_price(self.symbol)
        if latest:
            await self.send_json(latest)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,self.channel_name
        )
    
    async def stock_price_update(self, event):
        await self.send_json(event['data'])

    @database_sync_to_async
    def get_latest_price(self,symbol):
        try:
            today = date.today()
            bars = PriceBar.objects.filter(stock__symbol=symbol, timeframe='1d', timestamp__date=today).order_by('timestamp')
            
            if not bars.exists():
                bar = PriceBar.objects.filter(stock__symbol=symbol, timeframe='1d').last()
                if not bar:
                    return None
                return {
                    'symbol':symbol,
                    'open':float(bar.open),
                    'high':float(bar.high),
                    'low':float(bar.low),
                    'close':float(bar.close),
                    'volume':bar.volume,
                    'timestamp': str(bar.timestamp),
                    'candle':{
                        'time':bar.timestamp.strftime('%Y-%m-%d'),
                        'open':float(bar.open),
                        'high':float(bar.high),
                        'low':float(bar.low),
                        'close':float(bar.close),
                    }
                }
            first = bars.first()
            latest = bars.last()
            candle_open  = float(first.open)
            candle_high  = float(bars.order_by('-high').first().high)
            candle_low   = float(bars.order_by('low').first().low)
            candle_close = float(latest.close)

            return {
                'symbol': symbol,
                'open': candle_open,
                'high': candle_high,
                'low': candle_low,
                'close': candle_close,
                'volume': sum(b.volume for b in bars),
                'timestamp': str(latest.timestamp),
                # Candle for chart — backend builds it, frontend just calls update()
                'candle': {
                    'time': today.strftime('%Y-%m-%d'),
                    'open': candle_open,
                    'high': candle_high,
                    'low': candle_low,
                    'close': candle_close,
                }
            }
        except Exception:
            return None