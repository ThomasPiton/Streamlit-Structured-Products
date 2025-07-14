from base_wrapper import BaseWrapper

class Fund(BaseWrapper):
    """
    Wrapper class for a traditional Fund (e.g., mutual fund).

    Attributes:
        nav (float): Net Asset Value per unit.
        units (int): Number of units owned or issued.

    Example:
        Fund(nav=105.0, units=1000)
    """

    def __init__(self, nav: float, units: int):
        self.nav = nav
        self.units = units

    def price(self):
        """
        Calculate the total value of the fund.
        Returns:
            float: Total value = nav × units
        """
        return self.nav * self.units