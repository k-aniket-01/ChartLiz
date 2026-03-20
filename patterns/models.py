from django.db import models
from django.db import models
from stocks.models import Stock

class PatternDetection(models.Model):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    SIGNAL_CHOICES = [
        (BULLISH, "Bullish"),
        (BEARISH, "Bearish"),
        (NEUTRAL, "Neutral"),
    ]

    PATTERN_CHOICES = [
        ("doji",               "Doji"),
        ("hammer",             "Hammer"),
        ("shooting_star",      "Shooting Star"),
        ("bullish_engulfing",  "Bullish Engulfing"),
        ("bearish_engulfing",  "Bearish Engulfing"),
        ("morning_star",       "Morning Star"),
        ("evening_star",       "Evening Star"),
        ("three_white_soldiers", "Three White Soldiers"),
        ("three_black_crows",  "Three Black Crows"),
    ]

    stock        = models.ForeignKey(
                       Stock,
                       on_delete=models.CASCADE,
                       related_name="patterns"
                   )
    pattern_name = models.CharField(max_length=40, choices=PATTERN_CHOICES)
    signal       = models.CharField(max_length=10, choices=SIGNAL_CHOICES)
    candle_dt    = models.DateTimeField()
    timeframe    = models.CharField(max_length=5, default="1d")
    strength     = models.FloatField(default=0.0)
    detected_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-candle_dt"]
        unique_together = [("stock", "pattern_name", "candle_dt", "timeframe")]

    def __str__(self):
        return f"{self.stock.symbol} | {self.get_pattern_name_display()} | {self.candle_dt:%Y-%m-%d} | {self.signal}"
    

class PatternEducation(models.Model):
    pattern_name = models.CharField(max_length=40,choices=PatternDetection.PATTERN_CHOICES,unique=True)
    display_name = models.CharField(max_length=60)
    emoji = models.CharField(max_length=10, default='')
    signal = models.CharField(max_length=10, choices=PatternDetection.SIGNAL_CHOICES)
    one_liner = models.CharField(max_length=200)
    what_it_means = models.TextField()
    how_to_trade = models.TextField()
    reliability = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Pattern Education'
        verbose_name_plural = 'Pattern Education'
        ordering = ['pattern_name']

    def __str__(self):
        return self.display_name