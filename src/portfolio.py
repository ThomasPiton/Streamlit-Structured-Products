import numpy as np
import pandas as pd

class Portfolio:
    """Constructs an index portfolio and computes returns with rebalancing."""
    def __init__(self, price_df, weights, rebalance_freq='Monthly', txn_costs=None,
                 vol_target=None, vol_rebalance_freq=None, hedge_spot=False, hedge_fx=False):
        """
        price_df: DataFrame of index prices (columns = index names).
        weights: initial weights (list summing to 1).
        rebalance_freq: 'Daily','Weekly','Monthly','Quarterly','Yearly' or None for no rebalance.
        txn_costs: dict of transaction costs per index (in bps) or global cost as float.
        vol_target: target volatility (annualized).
        vol_rebalance_freq: frequency for adjusting volatility (if vol_target enabled).
        hedge_spot: bool for equity spot hedging (not fully implemented).
        hedge_fx: bool for FX hedging (not fully implemented).
        """
        self.price = price_df
        self.weights = np.array(weights)
        self.rebalance_freq = rebalance_freq
        self.txn_costs = txn_costs or {}
        self.vol_target = vol_target
        self.vol_rebalance_freq = vol_rebalance_freq
        self.hedge_spot = hedge_spot
        self.hedge_fx = hedge_fx
    
    def compute_returns(self):
        """
        Compute portfolio returns with optional rebalancing and transaction costs.
        Returns a Series of portfolio values (simulated). 
        """
        # Calculate daily returns of each index
        daily_ret = self.price.pct_change().fillna(0)
        dates = self.price.index
        port_val = 1.0
        port_vals = [port_val]
        current_weights = self.weights.copy()
        
        # Simulate day by day
        last_rebalance_date = dates[0]
        for i in range(1, len(dates)):
            date = dates[i]
            ret = np.dot(current_weights, daily_ret.iloc[i].fillna(0).values)
            # Apply volatility targeting (if enabled and at rebalance date)
            if self.vol_target is not None and self._is_rebalance(date, self.vol_rebalance_freq):
                # Estimate current vol (simple annualized vol of port from start)
                hist_rets = pd.Series(port_vals).pct_change().dropna()
                if len(hist_rets) > 1:
                    current_vol = hist_rets.std() * np.sqrt(252)
                    scale = self.vol_target / current_vol if current_vol > 0 else 1
                    current_weights = current_weights * scale
                    # Re-normalize if sum != 1 (keep direction)
                    current_weights = current_weights / np.sum(current_weights)
                    # Apply transaction cost for rebalancing (global cost)
                    if isinstance(self.txn_costs, (int,float)):
                        port_val -= port_val * (self.txn_costs / 10000)
            # If rebalance scheduled, set weights back to original or target (static here)
            if self._is_rebalance(date, self.rebalance_freq):
                current_weights = self.weights.copy()
                last_rebalance_date = date
            # Update portfolio value
            port_val = port_val * (1 + ret)
            port_vals.append(port_val)
        return pd.Series(port_vals, index=dates, name="Portfolio Value")
    
    def _is_rebalance(self, date, freq):
        """Helper to check if date triggers rebalance based on freq."""
        if not freq: return False
        if freq == 'Daily':
            return True
        if freq == 'Weekly' and date.weekday() == 0:  # Monday rebalance
            return True
        if freq == 'Monthly' and date.is_month_end:
            return True
        if freq == 'Quarterly' and date.is_quarter_end:
            return True
        if freq == 'Yearly' and date.is_year_end:
            return True
        return False