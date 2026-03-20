from django.db import migrations

EDUCATION_DATA = [
    {
        "pattern_name": "doji",
        "display_name": "Doji",
        "emoji":        "⚖️",
        "signal":       "neutral",
        "one_liner":    "Open and close at nearly the same price — market indecision.",
        "what_it_means": "A Doji forms when the opening and closing price are virtually equal, leaving a candle with a very small body. It signals that buyers and sellers are in equilibrium — neither side is winning. After a strong trend, a Doji can warn of a reversal.",
        "how_to_trade":  "Don't trade a Doji in isolation. Wait for the next candle to confirm direction. A bullish candle after a Doji in a downtrend = reversal signal. A bearish candle after a Doji in an uptrend = potential top.",
        "reliability":   "Medium — needs confirmation.",
    },
    {
        "pattern_name": "hammer",
        "display_name": "Hammer",
        "emoji":        "🔨",
        "signal":       "bullish",
        "one_liner":    "Long lower wick, small body at top — buyers rejected the lows.",
        "what_it_means": "A Hammer appears at the bottom of a downtrend. Price sold off sharply during the candle but recovered to close near the open. The long lower wick shows sellers tried to push lower but buyers stepped in hard.",
        "how_to_trade":  "Enter long above the Hammer's high. Place stop-loss below the wick low. Volume confirmation significantly improves the signal's reliability.",
        "reliability":   "Medium-High with volume confirmation.",
    },
    {
        "pattern_name": "shooting_star",
        "display_name": "Shooting Star",
        "emoji":        "⭐",
        "signal":       "bearish",
        "one_liner":    "Long upper wick at a top — buyers rejected the highs.",
        "what_it_means": "A Shooting Star has a long upper wick and forms at the top of an uptrend. Buyers pushed price up significantly but sellers slammed it back down by close, showing the bulls are losing control.",
        "how_to_trade":  "Enter short below the candle's low. Stop above the high of the wick. Best when it gaps up or forms after several strong bullish candles.",
        "reliability":   "High at clear resistance levels.",
    },
    {
        "pattern_name": "bullish_engulfing",
        "display_name": "Bullish Engulfing",
        "emoji":        "📈",
        "signal":       "bullish",
        "one_liner":    "Large green candle fully engulfs the prior red candle.",
        "what_it_means": "Day 1: a bearish candle. Day 2: a bullish candle whose body completely engulfs Day 1's body. Buyers overwhelmed sellers completely — a strong reversal signal from a downtrend.",
        "how_to_trade":  "Enter long at open of Day 3. Stop below the Day 2 low. Higher reliability when the Day 2 candle also has high volume. Even stronger at a key support level.",
        "reliability":   "High — one of the most reliable reversal signals.",
    },
    {
        "pattern_name": "bearish_engulfing",
        "display_name": "Bearish Engulfing",
        "emoji":        "📉",
        "signal":       "bearish",
        "one_liner":    "Large red candle fully engulfs the prior green candle.",
        "what_it_means": "Day 1: a bullish candle. Day 2: a bearish candle that completely engulfs Day 1. Sellers overwhelmed buyers — reversal signal at a top.",
        "how_to_trade":  "Enter short at open of Day 3. Stop above Day 2 high. Most effective at resistance levels after a strong uptrend.",
        "reliability":   "High — especially at resistance zones.",
    },
    {
        "pattern_name": "morning_star",
        "display_name": "Morning Star",
        "emoji":        "🌅",
        "signal":       "bullish",
        "one_liner":    "Three-candle bottom reversal: red, small body, big green.",
        "what_it_means": "Day 1: large bearish candle. Day 2: small-bodied candle (the star). Day 3: large bullish candle closing above Day 1's midpoint. One of the most powerful reversal signals.",
        "how_to_trade":  "Enter long at the close of Day 3 or open of Day 4. Stop below the Day 2 low. Volume should increase on Day 3.",
        "reliability":   "Very High — volume-confirmed at support.",
    },
    {
        "pattern_name": "evening_star",
        "display_name": "Evening Star",
        "emoji":        "🌇",
        "signal":       "bearish",
        "one_liner":    "Three-candle top reversal: green, small body, big red.",
        "what_it_means": "Mirror of Morning Star. Day 1: large bullish candle. Day 2: small-bodied star candle. Day 3: large bearish candle closing well below Day 1's midpoint.",
        "how_to_trade":  "Enter short at close of Day 3 or open of Day 4. Stop above Day 2 high. High volume Day 3 = much stronger signal.",
        "reliability":   "Very High — at clear resistance levels.",
    },
    {
        "pattern_name": "three_white_soldiers",
        "display_name": "Three White Soldiers",
        "emoji":        "🪖",
        "signal":       "bullish",
        "one_liner":    "Three consecutive strong bullish candles — bulls in full control.",
        "what_it_means": "Three large bullish candles, each closing near its own high. Shows sustained buying pressure over three sessions.",
        "how_to_trade":  "Confirm with RSI not overbought (below 70). Enter on break above the third candle's high. Beware of overextension.",
        "reliability":   "High for continuation — watch for overbought RSI.",
    },
    {
        "pattern_name": "three_black_crows",
        "display_name": "Three Black Crows",
        "emoji":        "🐦",
        "signal":       "bearish",
        "one_liner":    "Three consecutive strong bearish candles — bears dominating.",
        "what_it_means": "Three large bearish candles each closing near their own lows. Shows relentless selling pressure over three sessions.",
        "how_to_trade":  "Enter short at close of third candle or on pullback. Watch RSI — if already oversold (below 30), risk of counter-rally is high.",
        "reliability":   "High — one of the most bearish multi-candle patterns.",
    },
]


def seed_education(apps, schema_editor):
    PatternEducation = apps.get_model('patterns', 'PatternEducation')
    for data in EDUCATION_DATA:
        PatternEducation.objects.get_or_create(
            pattern_name=data['pattern_name'],
            defaults=data
        )


def unseed_education(apps, schema_editor):
    PatternEducation = apps.get_model('patterns', 'PatternEducation')
    PatternEducation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('patterns', '0002_patterneducation'),  # ← adjust to your actual previous migration
    ]

    operations = [
        migrations.RunPython(seed_education, unseed_education),
    ]