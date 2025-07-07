
class StructuredProduct:
    """Base class for structured products (e.g. autocallables, swaps)."""
    def __init__(self, underlying_portfolio):
        self.portfolio = underlying_portfolio
    
    def payoff(self, values):
        """Compute payoff given portfolio values (to be overridden)."""
        raise NotImplementedError("Subclasses implement payoff logic.")


class Autocallable(StructuredProduct):
    """A simple autocallable: pays coupon if above barrier, else continues."""
    def __init__(self, underlying_portfolio, barrier=1.0, coupon=0.05):
        super().__init__(underlying_portfolio)
        self.barrier = barrier
        self.coupon = coupon  # e.g., 5% coupon per year
    
    def payoff(self, port_values):
        # Simplified: if end value > barrier*initial, pay coupon, else pay final value
        init = port_values.iloc[0]
        final = port_values.iloc[-1]
        if final >= self.barrier * init:
            # Pay initial + coupon
            return init * (1 + self.coupon)
        else:
            return final


class Swap(StructuredProduct):
    """A simple equity swap: pay fixed leg, receive underlying."""
    def __init__(self, underlying_portfolio, fixed_rate=0.02):
        super().__init__(underlying_portfolio)
        self.fixed_rate = fixed_rate
    
    def payoff(self, port_values):
        # Simplified: calculate total return of portfolio vs fixed rate
        init = port_values.iloc[0]
        final = port_values.iloc[-1]
        underlying_return = (final / init) - 1
        swap_value = underlying_return - self.fixed_rate
        return swap_value