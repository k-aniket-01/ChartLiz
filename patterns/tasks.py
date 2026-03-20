import logging
import pandas as pd 
from celery import shared_task
from stocks.models import Stock, PriceBar
from patterns.services import PatternScanner
from patterns.models import PatternDetection

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, defualt_retry_delay=30)
def scan_patterns_for_stock(self, stock_id, timeframe='1d'):
    
    try:
        stock = Stock.objects.get(pk=stock_id)

        bars = (
            PriceBar.objects.filter(stock=stock,timeframe=timeframe).order_by('timestamp')
            .values('timestamp', 'open', 'high', 'low', 'close', 'volume')
        )

        if not bars:
            logger.warning("No bars found for stock_=%d", stock_id)
            return {'status':'skipped', 'reason':'no_bars'}
        
        df =  pd.DataFrame(list(bars)).set_index('timestamp')
        df.index = pd.to_datetime(df.index, utc=True)

        scanner = PatternScanner(df)
        results = scanner.detect_all()

        saved = 0 
        for r in results:
            obj, created = PatternDetection.objects.get_or_create(
                stock = stock,
                pattern_name = r['pattern_name'],
                candle_dt = r['candle_dt'],
                timeframe = timeframe,
                defaults = {'signal': r['signal']}
            )
            if created:
                saved += 1

        logger.info(
            "Pattern scan done — %s | %d found | %d new saved",
            stock.symbol, len(results), saved
        )

        return {
            'status':'ok',
            'symbol':stock.symbol,
            'pattern_found':len(results),
            'new_saved':saved
        }
    
    except Exception as exc:
        logger.exception("scan_patterns_for_stock failed for stock_id=%d", stock_id)
        raise self.retry(exc=exc)