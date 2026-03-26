from django.shortcuts import render, get_object_or_404
from django.http import Http404

# All pattern content in one place — no database needed
PATTERNS = {
    'hammer': {
        'name':        'Hammer',
        'slug':        'hammer',
        'signal':      'bullish',
        'description': 'A hammer forms when a stock opens, sells off sharply during the session, then recovers to close near the open. The long lower wick shows buyers overwhelmed sellers by the close.',
        'how_to_read': 'Look for a hammer after a downtrend. The lower wick should be at least 2x the body length. Confirm with the next candle closing higher before entering.',
        'entry':       'Buy on the open of the next candle after confirmation.',
        'stop_loss':   'Place stop below the low of the hammer candle.',
        'psychology':  'Sellers pushed price down hard, but buyers stepped in and reclaimed ground. Shows demand at that price level.',
        'reliability': 'Medium',
    },
    'doji': {
        'name':        'Doji',
        'slug':        'doji',
        'signal':      'neutral',
        'description': 'A doji forms when open and close are nearly equal, creating a cross shape. It signals indecision between buyers and sellers.',
        'how_to_read': 'A doji alone means nothing — context matters. After an uptrend it signals a potential reversal. After a downtrend it may signal exhaustion of sellers.',
        'entry':       'Wait for the next candle to confirm direction before entering.',
        'stop_loss':   'Place stop beyond the high or low of the doji depending on direction.',
        'psychology':  'Neither buyers nor sellers won the session. The market is at a decision point.',
        'reliability': 'Low — needs confirmation',
    },
    'engulfing-bullish': {
        'name':        'Bullish Engulfing',
        'slug':        'engulfing-bullish',
        'signal':      'bullish',
        'description': 'A two-candle pattern where a large green candle completely engulfs the previous red candle. Strong reversal signal after a downtrend.',
        'how_to_read': 'The second candle must open below the first candle\'s close and close above its open. Larger the engulfing candle, stronger the signal.',
        'entry':       'Enter at the close of the engulfing candle or open of the next candle.',
        'stop_loss':   'Place stop below the low of the engulfing candle.',
        'psychology':  'Buyers aggressively took control from sellers in a single session. Momentum has shifted.',
        'reliability': 'High — especially with volume confirmation',
    },
    'engulfing-bearish': {
        'name':        'Bearish Engulfing',
        'slug':        'engulfing-bearish',
        'signal':      'bearish',
        'description': 'A two-candle pattern where a large red candle completely engulfs the previous green candle. Strong reversal signal after an uptrend.',
        'how_to_read': 'The second candle must open above the first candle\'s close and close below its open. Signals sellers have taken over.',
        'entry':       'Enter short at the close of the engulfing candle or open of the next candle.',
        'stop_loss':   'Place stop above the high of the engulfing candle.',
        'psychology':  'Sellers aggressively took control from buyers. Uptrend momentum may be exhausted.',
        'reliability': 'High — especially with volume confirmation',
    },
    'shooting-star': {
        'name':        'Shooting Star',
        'slug':        'shooting-star',
        'signal':      'bearish',
        'description': 'A candle with a long upper wick and small body near the low. Forms after an uptrend — buyers pushed price up but sellers drove it back down by close.',
        'how_to_read': 'Upper wick should be at least 2x the body. Small or no lower wick. Appears after a series of rising candles.',
        'entry':       'Sell or short on the open of the next candle after confirmation.',
        'stop_loss':   'Place stop above the high of the shooting star.',
        'psychology':  'Buyers tried to extend the rally but were rejected hard. Shows supply at higher prices.',
        'reliability': 'Medium',
    },
    'morning-star': {
        'name':        'Morning Star',
        'slug':        'morning-star',
        'signal':      'bullish',
        'description': 'A three-candle reversal pattern. First: large red candle. Second: small candle gapping down (the star). Third: large green candle closing into the first candle\'s body.',
        'how_to_read': 'The middle candle shows indecision. The third candle\'s strength confirms buyers have taken over. Higher volume on the third candle strengthens the signal.',
        'entry':       'Enter at the close of the third candle or early in the next session.',
        'stop_loss':   'Place stop below the low of the middle star candle.',
        'psychology':  'Sellers exhausted themselves (candle 1), market was uncertain (candle 2), then buyers dominated (candle 3).',
        'reliability': 'High',
    },
    'evening-star': {
        'name':        'Evening Star',
        'slug':        'evening-star',
        'signal':      'bearish',
        'description': 'The bearish mirror of the morning star. First: large green candle. Second: small candle gapping up. Third: large red candle closing into the first candle\'s body.',
        'how_to_read': 'The third candle must close well into the first candle to confirm the reversal. Volume confirmation on the third candle adds reliability.',
        'entry':       'Sell or short at close of the third candle.',
        'stop_loss':   'Place stop above the high of the middle candle.',
        'psychology':  'Buyers ran out of steam, indecision followed, then sellers took firm control.',
        'reliability': 'High',
    },
    'three-white-soldiers': {
        'name':        'Three White Soldiers',
        'slug':        'three-white-soldiers',
        'signal':      'bullish',
        'description': 'Three consecutive large green candles, each opening within the previous candle\'s body and closing near its high. A strong bullish continuation or reversal signal.',
        'how_to_read': 'Each candle should have a small upper wick showing buyers were in control until close. Appears after a downtrend or consolidation period.',
        'entry':       'Enter on the open after the third soldier confirms.',
        'stop_loss':   'Place stop below the low of the first soldier candle.',
        'psychology':  'Three straight sessions of buyer dominance. Shows sustained momentum shift.',
        'reliability': 'High — but watch for overextension',
    },
    'hanging-man': {
        'name':        'Hanging Man',
        'slug':        'hanging-man',
        'signal':      'bearish',
        'description': 'Looks identical to a hammer but appears after an uptrend. The long lower wick shows sellers are beginning to push back despite buyers recovering by close.',
        'how_to_read': 'Context is everything — the same candle shape is bullish (hammer) in a downtrend and bearish (hanging man) in an uptrend. Confirm with the next red candle.',
        'entry':       'Sell or short after confirmation candle closes red.',
        'stop_loss':   'Place stop above the high of the hanging man.',
        'psychology':  'Sellers made a strong push during the session — a warning sign even though buyers recovered.',
        'reliability': 'Medium — requires confirmation',
    },
}


def pattern_list(request):
    patterns = list(PATTERNS.values())
    return render(request, 'education/pattern_list.html', {
        'patterns': patterns,
    })


def pattern_detail(request, slug):
    pattern = PATTERNS.get(slug)
    if not pattern:
        raise Http404(f'Pattern "{slug}" not found.')
    return render(request, 'education/pattern_detail.html', {
        'pattern': pattern,
    })