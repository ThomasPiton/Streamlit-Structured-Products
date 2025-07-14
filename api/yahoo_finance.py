import yfinance as yf

import yfinance as yf
import pandas as pd

class YahooFinance:
    """
    A class to fetch historical price data for a list of tickers from Yahoo Finance.

    Attributes
    ----------
    components : list of dict
        List of components with keys including 'ticker'.
    excess_return_benchmark : str or None
        Optional ticker symbol for excess return benchmark.
    benchmark_ticker : str or None
        Optional ticker symbol for benchmark.
    start_period : str or None
        Start date for historical data in 'YYYY-MM-DD' format.
    end_period : str or None
        End date for historical data in 'YYYY-MM-DD' format.

    Methods
    -------
    get_data()
        Fetches adjusted close price data for all relevant tickers and returns
        a DataFrame indexed by date with tickers as columns.
    """

    def __init__(self, **args):
        self.components = args.get("components", None)
        self.excess_return_benchmark = args.get("excess_return_benchmark", None)
        self.benchmark_ticker = args.get("benchmark_ticker", None)
        self.start_date = args.get("start_date", None)
        self.end_date = args.get("end_date", None)
        self.final_tickers = []
        self._process_inputs()

    def _process_inputs(self):
        """
        Prepares the list of all tickers to download by combining component tickers,
        excess return benchmark, and benchmark ticker (removing duplicates).
        """
        if not self.components or not isinstance(self.components, list):
            raise ValueError("components must be a list of dicts with at least 'ticker' key.")

        tickers = [comp["ticker"] for comp in self.components if comp.get("ticker")]
        if self.excess_return_benchmark:
            tickers.append(self.excess_return_benchmark)
        if self.benchmark_ticker:
            tickers.append(self.benchmark_ticker)

        # Remove duplicates while preserving order
        seen = set()
        self.final_tickers = [x for x in tickers if not (x in seen or seen.add(x))]

        if len(self.final_tickers) == 0:
            raise ValueError("No valid tickers found to download.")
    
    def get_data(self):
        """
        Downloads adjusted close price data for all tickers over the specified date range.

        Returns
        -------
        pd.DataFrame
            DataFrame indexed by date, columns are tickers with their adjusted close prices.
        """
        

        data = yf.download(
            tickers=self.final_tickers,
            start=self.start_date,
            end=self.end_date,
            progress=False,
            group_by='ticker',
            auto_adjust=True
        )

        # If only one ticker, yfinance returns a DataFrame with no ticker level, fix that:
        if len(self.final_tickers) == 1:
            df = data[["Close"]].rename(columns={"Close": self.final_tickers[0]})
        else:
            # For multiple tickers, data is multi-level columns: ticker / OHLCV
            # Extract Adjusted Close by taking 'Close' column (auto_adjust=True so Close = Adjusted Close)
            df = pd.DataFrame()
            for ticker in self.final_tickers:
                if ticker in data.columns.get_level_values(0):
                    df[ticker] = data[ticker]["Close"]
                else:
                    # If ticker missing in data (delisted or invalid), fill with NaN
                    df[ticker] = pd.NA

        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df
    
    
    def get_currency(self):
        result = []
        for ticker in self.final_tickers:
            try:
                result.append(yf.Ticker(ticker).fast_info.get("currency"))
            except Exception as e:
                return None