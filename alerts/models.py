from django.db import models
from django.conf import settings

# Create your models here.
class Alert(models.Model):
    ALERT_TYPES = [
        ('price_above', 'Price Above'),
        ('price_below', 'Price Below'),
        ('pattern', 'Pattern Detected'),
        ('rsi_above', 'RSI Above'),
        ('rsi_below', 'RSI Below'),
        ('macd_cross_up', 'MACD Bullish Cross'),
        ('macd_cross_dn', 'MACD Bearish Cross'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alters')
    symbol = models.CharField(max_length=20)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    threshold = models.DecimalField(max_digits=16, decimal_places=4, null=True, blank=True)
    pattern_name = models.CharField(max_length=60, blank=True)
    is_active = models.BooleanField(default=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} | {self.symbol} | {self.alert_type}"
    
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    alert = models.ForeignKey(Alert, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=120)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} | {self.title} | read= {self.is_read}"
    