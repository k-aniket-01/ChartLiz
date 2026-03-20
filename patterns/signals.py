import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from stocks.models import PriceBar

logger = logging.getLogger(__name__)

@receiver(post_save, sender=PriceBar)
def trigger_pattern_scan(sender, instance, created, **kwargs):
    if not created:
        return
    
    from patterns.tasks import scan_patterns_for_stock

    scan_patterns_for_stock.apply_async(
        args=[instance.stock_id, instance.timeframe],
        countdown=2
    )
    logger.debug(
        "Queued pattern scan for stock_id=%d timeframe=%s",
        instance.stock_id,
        instance.timeframe
    )