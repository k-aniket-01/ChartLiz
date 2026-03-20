import logging
import numpy as np
import pandas as pd

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
        o = self.df["open"]
        h = self.df["high"]
        l = self.df["low"]
        c = self.df["close"]

        self.body         = (c - o).abs()
        self.candle_range = h - l
        self.upper_wick   = h - pd.concat([o, c], axis=1).max(axis=1)
        self.lower_wick   = pd.concat([o, c], axis=1).min(axis=1) - l
        self.is_bullish   = c > o
        self.is_bearish   = c < o
        self.avg_body     = self.body.rolling(14).mean()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _small_body(self, factor=0.3):
        return self.body < (self.avg_body * factor)

    def _large_body(self, factor=0.7):
        return self.body > (self.candle_range * factor)

    # ── Strength scoring (Task 7) ─────────────────────────────────────────────

    def _score(self, candle_dt) -> float:
        """
        Scores a detected pattern 0.0–1.0 based on three factors:
          1. Volume confirmation  (0–0.40 pts)
          2. Trend context        (0–0.40 pts)
          3. Candle size filter   (0–0.20 pts)
        """
        try:
            idx = self.df.index.get_loc(candle_dt)
        except KeyError:
            return 0.5

        score = 0.0

        # ── Factor 1: Volume confirmation ────────────────────────────────────
        # Higher volume on the pattern candle = stronger conviction
        vol_window = self.df["volume"].iloc[max(0, idx - 19): idx + 1]
        if len(vol_window) >= 2:
            avg_vol = vol_window[:-1].mean()   # average of previous candles
            cur_vol = vol_window.iloc[-1]      # this candle's volume
            if avg_vol > 0:
                vol_ratio = cur_vol / avg_vol
                # Cap at 3× — anything beyond gets full score
                score += min(vol_ratio / 3.0, 1.0) * 0.40

        # ── Factor 2: Trend context ───────────────────────────────────────────
        # Counter-trend reversals are more significant than continuations
        close_window = self.df["close"].iloc[max(0, idx - 9): idx + 1]
        if len(close_window) >= 5:
            # polyfit returns [slope, intercept] — slope tells us trend direction
            slope        = np.polyfit(range(len(close_window)), close_window.values, 1)[0]
            trend_is_up  = slope > 0
            candle_is_bullish = bool(self.is_bullish.iloc[idx])

            if (candle_is_bullish and not trend_is_up) or \
               (not candle_is_bullish and trend_is_up):
                score += 0.40   # counter-trend reversal — high significance
            else:
                score += 0.20   # same direction — moderate significance

        # ── Factor 3: Candle size filter ─────────────────────────────────────
        # Larger candle relative to recent average = stronger signal
        recent_bodies = self.body.iloc[max(0, idx - 13): idx + 1]
        if len(recent_bodies) >= 2:
            avg_body = recent_bodies[:-1].mean()
            cur_body = recent_bodies.iloc[-1]
            if avg_body > 0:
                size_ratio = cur_body / avg_body
                score += min(size_ratio / 2.0, 1.0) * 0.20

        return round(min(score, 1.0), 4)

    # ── Pattern detectors ─────────────────────────────────────────────────────

    def _detect_doji(self):
        mask = self.body < (self.candle_range * 0.10)
        return self.df.index[mask], "neutral"

    def _detect_hammer(self):
        small_upper = self.upper_wick < (self.body * 0.3)
        long_lower  = self.lower_wick > (self.body * 2)
        body_top    = self._small_body()
        mask = small_upper & long_lower & body_top
        return self.df.index[mask], "bullish"

    def _detect_shooting_star(self):
        small_lower = self.lower_wick < (self.body * 0.3)
        long_upper  = self.upper_wick > (self.body * 2)
        body_small  = self._small_body()
        mask = small_lower & long_upper & body_small
        return self.df.index[mask], "bearish"

    def _detect_bullish_engulfing(self):
        o = self.df["open"]
        c = self.df["close"]
        prev_bearish  = self.is_bearish.shift(1)
        today_bullish = self.is_bullish
        engulfs       = (c > o.shift(1)) & (o < c.shift(1))
        mask = prev_bearish & today_bullish & engulfs
        return self.df.index[mask], "bullish"

    def _detect_bearish_engulfing(self):
        o = self.df["open"]
        c = self.df["close"]
        prev_bullish  = self.is_bullish.shift(1)
        today_bearish = self.is_bearish
        engulfs       = (c < o.shift(1)) & (o > c.shift(1))
        mask = prev_bullish & today_bearish & engulfs
        return self.df.index[mask], "bearish"

    def _detect_morning_star(self):
        c = self.df["close"]
        o = self.df["open"]
        day1_bearish = self.is_bearish.shift(2) & self._large_body().shift(2)
        day2_small   = self._small_body().shift(1)
        day3_bullish = self.is_bullish & self._large_body()
        day1_mid     = ((o.shift(2) + c.shift(2)) / 2)
        closes_above = c > day1_mid
        mask = day1_bearish & day2_small & day3_bullish & closes_above
        return self.df.index[mask], "bullish"

    def _detect_evening_star(self):
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
        c = self.df["close"]
        three_bearish = (
            self.is_bearish &
            self.is_bearish.shift(1) &
            self.is_bearish.shift(2)
        )
        each_lower = (c < c.shift(1)) & (c.shift(1) < c.shift(2))
        each_large = (
            self._large_body() &
            self._large_body().shift(1) &
            self._large_body().shift(2)
        )
        mask = three_bearish & each_lower & each_large
        return self.df.index[mask], "bearish"

    # ── Main entry point ──────────────────────────────────────────────────────

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
                        "strength":     self._score(dt),   # ← Task 7
                    })
            except Exception as exc:
                logger.exception("Detector %s failed: %s", detector.__name__, exc)

        return results