from base_wrapper import BaseWrapper

class ETF(BaseWrapper):
    """
    Wrapper class for an Exchange-Traded Fund (ETF).

    Attributes:
        market_price (float): The current price of one ETF share in the market.
        shares_outstanding (int): The total number of shares issued.

    Example:
        ETF(market_price=25.5, shares_outstanding=100000)
    """

    def __init__(self, market_price: float, shares_outstanding: int):
        self.market_price = market_price
        self.shares_outstanding = shares_outstanding

    def price(self):
        """
        Calculate the total market capitalization of the ETF.
        Returns:
            float: Total value = market_price × shares_outstanding
        """
        return self.market_price * self.shares_outstanding