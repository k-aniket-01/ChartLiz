from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.utils import timezone
from patterns.models import PatternDetection, PatternEducation
from stocks.models import Stock


@login_required
def pattern_markers_api(request, symbol):
    stock     = get_object_or_404(Stock, symbol=symbol.upper())
    timeframe = request.GET.get('timeframe', '1d')
    days      = int(request.GET.get('days', 365))
    since     = timezone.now() - timedelta(days=days)

    patterns = PatternDetection.objects.filter(
        stock=stock,
        timeframe=timeframe,
        candle_dt__gte=since,
    ).order_by('candle_dt')

    markers = []
    for p in patterns:
        if p.signal == 'bullish':
            color    = '#3ecf8e'
            position = 'belowBar'
            shape    = 'arrowUp'
        elif p.signal == 'bearish':
            color    = '#f87171'
            position = 'aboveBar'
            shape    = 'arrowDown'
        else:
            color    = '#f59e0b'
            position = 'belowBar'
            shape    = 'circle'

        markers.append({
            'time':         int(p.candle_dt.timestamp()),
            'position':     position,
            'color':        color,
            'shape':        shape,
            'text':         p.get_pattern_name_display(),
            'pattern_name': p.pattern_name,
            'signal':       p.signal,
        })

    return JsonResponse({'markers': markers})


class PatternHistoryView(LoginRequiredMixin, ListView):
    model               = PatternDetection
    template_name       = 'patterns/history.html'
    context_object_name = 'patterns'
    paginate_by         = 20

    def get_queryset(self):
        symbol         = self.kwargs['symbol'].upper()
        self.stock     = get_object_or_404(Stock, symbol=symbol)
        timeframe      = self.request.GET.get('timeframe', '1d')
        signal_filter  = self.request.GET.get('signal', '')
        pattern_filter = self.request.GET.get('pattern', '')  # ← fixed typo

        qs = (
            PatternDetection.objects
            .filter(stock=self.stock, timeframe=timeframe)
            .order_by('-candle_dt')
        )

        if signal_filter in ('bullish', 'bearish', 'neutral'):
            qs = qs.filter(signal=signal_filter)              # ← fixed: was filtering pattern_name

        if pattern_filter:
            qs = qs.filter(pattern_name=pattern_filter)       # ← fixed typo

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Safety fallback in case get_queryset hasn't set self.stock yet
        stock = getattr(self, 'stock', None)
        if stock is None:
            symbol     = self.kwargs['symbol'].upper()
            stock      = get_object_or_404(Stock, symbol=symbol)
            self.stock = stock

        ctx['stock']        = self.stock
        ctx['timeframe']    = self.request.GET.get('timeframe', '1d')
        ctx['signal']       = self.request.GET.get('signal', '')
        ctx['pattern']      = self.request.GET.get('pattern', '')
        ctx['all_patterns'] = PatternDetection.PATTERN_CHOICES
        ctx['timeframes']   = ['1d', '1h', '5m']
        ctx['total_count']  = PatternDetection.objects.filter(
            stock=self.stock
        ).count()
        return ctx
    
def pattern_detail_api(request, pattern_name):
    try:
        edu = PatternEducation.objects.get(pattern_name=pattern_name)
        return JsonResponse({
            'display_name':edu.display_name,
            'emoji':edu.emoji,
            'signal':edu.signal,
            'one_liner':edu.one_liner,
            'what_it_means':edu.what_it_means,
            'how_to_trade':edu.how_to_trade,
            'reliability':edu.reliability
        })
    except PatternEducation.DoesNotExist:
        return JsonResponse({'error': f'Unknown pattern: {pattern_name}'}, status=404)