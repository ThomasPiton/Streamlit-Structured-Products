# metrics_module.py
import numpy as np

def annualized_return(cumulative_values, periods_per_year=252):
    """
    Calculate annualized return given cumulative portfolio values.
    Assumes the first value is at time 0.
    """
    n = len(cumulative_values) - 1
    if n <= 0:
        return np.nan
    total_ret = cumulative_values.iloc[-1] / cumulative_values.iloc[0]
    return total_ret ** (periods_per_year / n) - 1

def annualized_volatility(returns, periods_per_year=252):
    """Annualized standard deviation of returns."""
    return returns.std() * np.sqrt(periods_per_year)

def sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252):
    """Sharpe ratio = (mean(excess returns) / std) annualized."""
    excess_returns = returns - (risk_free_rate / periods_per_year)
    # Annualized return and vol
    ann_ret = np.mean(excess_returns) * periods_per_year
    ann_vol = np.std(excess_returns) * np.sqrt(periods_per_year)
    if ann_vol == 0:
        return np.nan
    return ann_ret / ann_vol

def information_ratio(returns, benchmark_returns):
    """Information ratio = (mean(port_excess) / std of port_excess) annualized."""
    ex_ret = returns - benchmark_returns
    # Tracking error = std of excess returns
    if len(ex_ret) < 2:
        return np.nan
    return np.mean(ex_ret) / np.std(ex_ret)

def max_drawdown(cumulative_values):
    """Maximum drawdown from peak in a cumulative value series."""
    cum = cumulative_values
    high_water_mark = cum.cummax()
    drawdown = (cum - high_water_mark) / high_water_mark
    return drawdown.min()

def calmar_ratio(cumulative_values, periods_per_year=252):
    """Calmar ratio = annualized return / absolute(max drawdown)."""
    ann_ret = annualized_return(cumulative_values, periods_per_year)
    mdd = abs(max_drawdown(cumulative_values))
    if mdd == 0:
        return np.nan
    return ann_ret / mdd
