import numpy as np
import pandas as pd
import yfinance as yf

class LevelIndex:
    def __init__(self, data: pd.DataFrame, params: dict):
        """
        data: DataFrame with all necessary columns:
              - component close prices (e.g., 'AAPL', 'MSFT', ...)
              - optional 'dividend_{ticker}', 'benchmark', 'fx_{ticker}', etc.
        params: configuration dictionary
        """
        self.data = data.copy()
        self.params = params
        self.components = params["components"]
        self.weights = np.array([c["weight"] for c in self.components]) / 100
        self.return_type = params["return_type"]
        self.base_level = 100.0

    def compute(self):
        tickers = [c["ticker"] for c in self.components]
        prices = self.data[tickers].copy()

        # FX conversion if needed
        # if "index_currency" in self.params:
        #     index_ccy = self.params["index_currency"]
        #     for ticker in tickers:
        #         fx_col = f"fx_{ticker}"
        #         if fx_col in self.data.columns:
        #             prices[ticker] *= self.data[fx_col]  # Convert to index currency

        # Price returns
        price_returns = prices.pct_change().fillna(0)
        weighted_price_return = price_returns.dot(self.weights)

        # Adjust return type
        total_return = weighted_price_return.copy()

        if self.return_type == "Price Return":
            pass

        elif self.return_type == "Excess Return":
            benchmark_col = self.params["excess_return_benchmark"]
            if benchmark_col not in self.data.columns:
                raise ValueError(f"Missing benchmark column: {benchmark_col}")
            benchmark_daily_rate = self.data[benchmark_col] / 100 / 252  # annual to daily
            total_return -= benchmark_daily_rate.fillna(0)

        elif self.return_type == "Total Return":
            total_return += self._aggregate_dividends(gross=True)

        elif self.return_type == "Net Total Return":
            withholding = self.params.get("withholding_rate", 15.0) / 100
            total_return += self._aggregate_dividends(gross=False, withholding=withholding)

        elif self.return_type == "Gross Return":
            total_return += self._aggregate_dividends(gross=True)

        elif self.return_type == "Synthetic Dividend Total Return":
            level = self.params.get("synthetic_dividend_level", 2.0) / 100  # % per year
            daily_dividend = level / 252
            total_return += daily_dividend

        else:
            raise ValueError(f"Unsupported return type: {self.return_type}")

        # Apply volatility targeting if enable
        # d
        if self.params.get("use_vol_target", False):
            total_return = self._apply_volatility_targeting(total_return)

        # Compute index level
        index_level = (1 + total_return).cumprod() * self.base_level
        df = pd.DataFrame({"index_value": index_level}).reset_index()
        return df

    def _aggregate_dividends(self, gross=True, withholding=0.15):
        tickers = [c["ticker"] for c in self.components]
        total_div = pd.Series(0, index=self.data.index)

        for i, ticker in enumerate(tickers):
            col = f"dividend_{ticker}"
            if col in self.data.columns:
                div = self.data[col].fillna(0)
                if not gross:
                    div *= (1 - withholding)
                total_div += div * self.weights[i]

        return total_div

    def _apply_volatility_targeting(self, returns: pd.Series):
        target = self.params["target_vol"] / 100
        window = self.params["vol_window"]
        method = self.params["vol_method"]

        if method == "Historical":
            vol = returns.rolling(window).std()
        elif method == "Exponential":
            vol = returns.ewm(span=window).std()
        else:
            raise ValueError(f"Unsupported vol method: {method}")

        leverage = (target / vol).clip(upper=3.0)
        return returns * leverage.shift(1).fillna(1.0)