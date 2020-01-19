import pandas as _pd
from typing import Union

# create convenient type hint
PANDAS = Union[_pd.DataFrame, _pd.Series]


def ta_sma(df: PANDAS, period=12):
    return df.rolling(period).mean()


def ta_ema(df: PANDAS, period=12):
    return df.ewm(span=period, adjust=False, min_periods=period-1).mean()


def ta_macd(df: PANDAS, fast_period=12, slow_period=26, signal_period=9, relative=True):
    fast = ta_ema(df, fast_period)
    slow = ta_ema(df, slow_period)
    macd = (fast / slow - 1) if relative else (fast - slow)
    signal = ta_ema(macd, signal_period)
    hist = macd - signal

    for label, frame in {"macd": macd, "signal": signal, "histogram": hist}.items():
        if isinstance(frame, _pd.DataFrame) and len(df.columns) > 1:
            frame.columns = _pd.MultiIndex.from_product([frame.columns, [label]])
        else:
            frame.name = label

    macd = macd.to_frame() if isinstance(macd, _pd.Series) else macd
    return macd.join(signal).join(hist)


def ta_mom(df: PANDAS, period=10):
    return df.diff(period)


def ta_roc(df: PANDAS, period=10):
    return df.pct_change(period)


def ta_apo(df: PANDAS, fast_period=12, slow_period=26, exponential=False):
    fast = ta_ema(df, fast_period) if exponential else ta_sma(df, fast_period)
    slow = ta_ema(df, slow_period) if exponential else ta_sma(df, slow_period)
    return fast - slow


def ta_trix(df: PANDAS, period=30):
    return ta_ema(ta_ema(ta_ema(df, period), period), period).pct_change() * 100


def ta_tr(df: PANDAS, high="High", low="Low", close="Close", relative=False):
    h = df[high]
    l = df[low]
    c = df[close].shift(1)

    if relative:
        ranges = (h / l - 1).rename("a").to_frame() \
            .join((h / c - 1).rename("b").abs()) \
            .join((l / c - 1).rename("c").abs())
    else:
        ranges = (h - l).rename("a").to_frame()\
            .join((h - c).rename("b").abs())\
            .join((l - c).rename("c").abs())

    return ranges.max(axis=1).rename("true_range")


def ta_atr(df: PANDAS, period=14, high="High", low="Low", close="Close", relative=False, exponential='wilder'):
    if exponential is True:
        return ta_ema(ta_tr(df, high, low, close, relative), period)
    if exponential == 'wilder':
        return ta_ema(ta_tr(df, high, low, close, relative), period * 2 - 1)
    else:
        return ta_sma(ta_tr(df, high, low, close, relative), period)


def ta_adx(df: PANDAS, period=14, high="High", low="Low", close="Close"):
    smooth = period * 2 - 1

    temp = _pd.DataFrame({
        "up": df[high] - df[high].shift(1),
        "down": df[low].shift(1) - df[low]
    }, index=df.index)

    atr = ta_atr(df, period, high, low, close, relative=False)
    pdm = ta_ema(temp.apply(lambda r: r[0] if r["up"] > r["down"] and r["up"] > 0 else 0, raw=False, axis=1), smooth)
    ndm = ta_ema(temp.apply(lambda r: r[1] if r["down"] > r["up"] and r["down"] > 0 else 0, raw=False, axis=1), smooth)

    pdi = pdm / atr
    ndi = ndm / atr
    adx = ta_ema((pdi - ndi).abs() / (pdi + ndi).abs(), smooth)

    return _pd.DataFrame({"+DM": pdm, "-DM": ndm, "+DI": pdi, "-DI": ndi, "ADX": adx}, index=df.index)
