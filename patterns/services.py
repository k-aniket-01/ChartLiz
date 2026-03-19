import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class PatternScanner:

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = self._normalise(df.copy())
        self._prepare_metrics()

    @staticmethod
    def _normalise(df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [c.lower() for c in df.columns]
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        return df.dropna(subset=["open", "high", "low", "close"])

    def _prepare_metrics(self):
        """
        Pre-calculate reusable candle measurements.
        These are pandas Series — one value per candle row.
        """
        o = self.df["open"]
        h = self.df["high"]
        l = self.df["low"]
        c = self.df["close"]

        self.body        = (c - o).abs()                  # size of the candle body
        self.candle_range = h - l                          # full high-low range
        self.upper_wick  = h - pd.concat([o, c], axis=1).max(axis=1)
        self.lower_wick  = pd.concat([o, c], axis=1).min(axis=1) - l
        self.is_bullish  = c > o                           # green candle
        self.is_bearish  = c < o                           # red candle

        # Average body size over last 14 candles — used to judge "small" vs "large"
        self.avg_body = self.body.rolling(14).mean()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _small_body(self, factor=0.3):
        """Body is less than factor × average body (relatively small candle)."""
        return self.body < (self.avg_body * factor)

    def _large_body(self, factor=0.7):
        """Body is larger than factor × candle range (dominant candle)."""
        return self.body > (self.candle_range * factor)

    # ── Pattern detectors ────────────────────────────────────────────────────

    def _detect_doji(self):
        """Body is less than 5% of the candle range — indecision."""
        mask = self.body < (self.candle_range * 0.05)
        return self.df.index[mask], "neutral"

    def _detect_hammer(self):
        """
        Bullish reversal at a low.
        - Small body in the upper third of the range
        - Lower wick at least 2× the body
        - Tiny upper wick
        """
        small_upper = self.upper_wick < (self.body * 0.3)
        long_lower  = self.lower_wick > (self.body * 2)
        body_top    = self._small_body()
        mask = small_upper & long_lower & body_top
        return self.df.index[mask], "bullish"

    def _detect_shooting_star(self):
        """
        Bearish reversal at a high.
        - Small body in the lower third of the range
        - Upper wick at least 2× the body
        - Tiny lower wick
        """
        small_lower = self.lower_wick < (self.body * 0.3)
        long_upper  = self.upper_wick > (self.body * 2)
        body_small  = self._small_body()
        mask = small_lower & long_upper & body_small
        return self.df.index[mask], "bearish"

    def _detect_bullish_engulfing(self):
        """
        Day 1: bearish candle. Day 2: bullish candle that fully engulfs Day 1.
        """
        o = self.df["open"]
        c = self.df["close"]
        prev_bearish = self.is_bearish.shift(1)            # yesterday was red
        today_bullish = self.is_bullish                    # today is green
        engulfs = (c > o.shift(1)) & (o < c.shift(1))     # today's body covers yesterday's body
        mask = prev_bearish & today_bullish & engulfs
        return self.df.index[mask], "bullish"

    def _detect_bearish_engulfing(self):
        """
        Day 1: bullish candle. Day 2: bearish candle that fully engulfs Day 1.
        """
        o = self.df["open"]
        c = self.df["close"]
        prev_bullish = self.is_bullish.shift(1)
        today_bearish = self.is_bearish
        engulfs = (c < o.shift(1)) & (o > c.shift(1))
        mask = prev_bullish & today_bearish & engulfs
        return self.df.index[mask], "bearish"

    def _detect_morning_star(self):
        """
        3-candle bullish reversal:
        Day 1: large bearish. Day 2: small body (the star). Day 3: large bullish.
        """
        c = self.df["close"]
        o = self.df["open"]
        day1_bearish = self.is_bearish.shift(2) & self._large_body().shift(2)
        day2_small   = self._small_body().shift(1)
        day3_bullish = self.is_bullish & self._large_body()
        # Day 3 must close above Day 1's midpoint
        day1_mid     = ((o.shift(2) + c.shift(2)) / 2)
        closes_above = c > day1_mid
        mask = day1_bearish & day2_small & day3_bullish & closes_above
        return self.df.index[mask], "bullish"

    def _detect_evening_star(self):
        """
        3-candle bearish reversal — mirror of Morning Star.
        """
        c = self.df["close"]
        o = self.df["open"]
        day1_bullish = self.is_bullish.shift(2) & self._large_body().shift(2)
        day2_small   = self._small_body().shift(1)
        day3_bearish = self.is_bearish & self._large_body()
        day1_mid     = ((o.shift(2) + c.shift(2)) / 2)
        closes_below = c < day1_mid
        mask = day1_bullish & day2_small & day3_bearish & closes_below
        return self.df.index[mask], "bearish"

    def _detect_three_white_soldiers(self):
        """
        3 consecutive large bullish candles, each closing higher.
        """
        c = self.df["close"]
        three_bullish = (
            self.is_bullish &
            self.is_bullish.shift(1) &
            self.is_bullish.shift(2)
        )
        each_higher = (c > c.shift(1)) & (c.shift(1) > c.shift(2))
        each_large  = (
            self._large_body() &
            self._large_body().shift(1) &
            self._large_body().shift(2)
        )
        mask = three_bullish & each_higher & each_large
        return self.df.index[mask], "bullish"

    def _detect_three_black_crows(self):
        """
        3 consecutive large bearish candles, each closing lower.
        """
        c = self.df["close"]
        three_bearish = (
            self.is_bearish &
            self.is_bearish.shift(1) &
            self.is_bearish.shift(2)
        )
        each_lower  = (c < c.shift(1)) & (c.shift(1) < c.shift(2))
        each_large  = (
            self._large_body() &
            self._large_body().shift(1) &
            self._large_body().shift(2)
        )
        mask = three_bearish & each_lower & each_large
        return self.df.index[mask], "bearish"

    # ── Main entry point ─────────────────────────────────────────────────────

    def detect_all(self) -> list:
        if len(self.df) < 3:
            logger.warning("Need at least 3 candles, got %d", len(self.df))
            return []

        detectors = [
            self._detect_doji,
            self._detect_hammer,
            self._detect_shooting_star,
            self._detect_bullish_engulfing,
            self._detect_bearish_engulfing,
            self._detect_morning_star,
            self._detect_evening_star,
            self._detect_three_white_soldiers,
            self._detect_three_black_crows,
        ]

        results = []
        for detector in detectors:
            try:
                timestamps, signal = detector()
                pattern_name = detector.__name__.replace("_detect_", "")
                for dt in timestamps:
                    results.append({
                        "pattern_name": pattern_name,
                        "signal":       signal,
                        "candle_dt":    dt,
                    })
            except Exception as exc:
                logger.exception("Detector %s failed: %s", detector.__name__, exc)

        return results