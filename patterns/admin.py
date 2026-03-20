from django.contrib import admin
from patterns.models import PatternDetection, PatternEducation

@admin.register(PatternDetection)
class PatternDetectionAdmin(admin.ModelAdmin):
    list_display = ('stock', 'candle_dt', 'pattern_name', 'signal', 'timeframe')
    list_filter = ('signal', 'pattern_name', 'timeframe')
    search_fields = ('stock_symbol',)
    ordering = ('-candle_dt',)

@admin.register(PatternEducation)
class PatternEducation(admin.ModelAdmin):
    list_display = ('emoji', 'display_name', 'signal', 'reliability')
    list_filter = ('signal',)
    ordering = ('pattern_name',)

    # Makes text fields bigger in admin
    fieldsets = [
        (None, {
            'fields':('pattern_name', 'display_name', 'emoji', 'signal')
        }),
        ('Content', {
            'fields':('one_liner', 'what_it_means', 'how_to_trade', 'reliability')
        }),
    ]
