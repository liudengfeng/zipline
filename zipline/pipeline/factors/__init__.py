from .factor import (
    CustomFactor,
    Factor,
    Latest,
    RecarrayField,
)
from .basic import (
    AnnualizedVolatility,
    AverageDollarVolume,
    DailyReturns,
    EWMA,
    ExponentialWeightedMovingAverage,
    ExponentialWeightedMovingStdDev,
    EWMSTD,
    LinearWeightedMovingAverage,
    MaxDrawdown,
    PeerCount,
    PercentChange,
    Returns,
    SimpleMovingAverage,
    VWAP,
    WeightedAverageValue,
)
from .events import (
    BusinessDaysSincePreviousEvent,
    BusinessDaysUntilNextEvent,
)
from .statistical import (
    RollingLinearRegressionOfReturns,
    RollingPearsonOfReturns,
    RollingSpearmanOfReturns,
    SimpleBeta,
)
from .technical import (
    Aroon,
    BollingerBands,
    FastStochasticOscillator,
    IchimokuKinkoHyo,
    MACDSignal,
    MovingAverageConvergenceDivergenceSignal,
    RateOfChangePercentage,
    RSI,
    TrueRange,
)

# 🆗 平均成交额
AverageAmount = AverageDollarVolume

__all__ = [
    'AnnualizedVolatility',
    'Aroon',
    'AverageDollarVolume',
    'BollingerBands',
    'BusinessDaysSincePreviousEvent',
    'BusinessDaysUntilNextEvent',
    'CustomFactor',
    'DailyReturns',
    'EWMA',
    'EWMSTD',
    'ExponentialWeightedMovingAverage',
    'ExponentialWeightedMovingStdDev',
    'Factor',
    'FastStochasticOscillator',
    'IchimokuKinkoHyo',
    'Latest',
    'LinearWeightedMovingAverage',
    'MACDSignal',
    'MaxDrawdown',
    'MovingAverageConvergenceDivergenceSignal',
    'PercentChange',
    'PeerCount',
    'RateOfChangePercentage',
    'RecarrayField',
    'Returns',
    'RollingLinearRegressionOfReturns',
    'RollingPearsonOfReturns',
    'RollingSpearmanOfReturns',
    'RSI',
    'SimpleBeta',
    'SimpleMovingAverage',
    'TrueRange',
    'VWAP',
    'WeightedAverageValue',
]
