# main_app.py
import streamlit as st
import pandas as pd
from data_module import DataLoader
from portfolio_module import Portfolio, Autocallable, Swap
from backtest_module import Backtester
from config import save_simulation, load_simulation
from metrics_module import max_drawdown

st.title("Structured Products Simulator")

# Sidebar: Data selection
st.sidebar.header("1. Load Data")
data_loader = DataLoader()

uploaded_files = st.sidebar.file_uploader(
    "Upload up to 5 index CSV files", type="csv", accept_multiple_files=True
)
if uploaded_files:
    if len(uploaded_files) > 5:
        st.sidebar.error("Please upload at most 5 files.")
    for file in uploaded_files:
        name = file.name.rstrip(".csv")
        data_loader.load_from_csv(name, file)

# Return type selection
ret_type = st.sidebar.selectbox(
    "Index Return Type", options=["price", "total", "net_total", "excess"]
)
risk_free = None
if ret_type == "excess":
    risk_free_file = st.sidebar.file_uploader("Upload Risk-Free CSV", type="csv")
    if risk_free_file:
        rf_df = pd.read_csv(risk_free_file, parse_dates=['Date']).set_index('Date').sort_index()
        risk_free = rf_df['Close']
bench = st.sidebar.checkbox("Include Benchmark?")
benchmark_name = None
if bench:
    benchmark_name = st.sidebar.text_input("Benchmark Index Name (uploaded)")

# Dynamic basket construction
st.sidebar.header("2. Portfolio Construction")
index_names = list(data_loader.data.keys())
selected_indices = st.sidebar.multiselect("Select Indices for Basket", index_names)
weights = None
if selected_indices:
    default_w = 1.0 / len(selected_indices)
    weights = []
    for idx in selected_indices:
        w = st.sidebar.number_input(f"Weight for {idx}", min_value=0.0, max_value=1.0, value=default_w, step=0.05)
        weights.append(w)
    # Normalize weights
    total_w = sum(weights)
    if total_w > 0:
        weights = [w/total_w for w in weights]

# Rebalancing and costs
st.sidebar.header("3. Strategy Options")
rebalance_freq = st.sidebar.selectbox("Rebalance Frequency",
    options=[None, 'Daily','Weekly','Monthly','Quarterly','Yearly'], index=3)
static_weights = st.sidebar.checkbox("Static weights (no rebalance)", value=False)
if static_weights:
    rebalance_freq = None  # override
txn_choice = st.sidebar.selectbox("Transaction Cost", options=["None","Per Index","Global"])
txn_costs = None
if txn_choice == "Per Index":
    txn_costs = {}
    for idx in selected_indices:
        cost = st.sidebar.number_input(f"Tx cost (bps) for {idx}", min_value=0.0, value=0.0, step=0.1)
        txn_costs[idx] = cost
elif txn_choice == "Global":
    global_cost = st.sidebar.number_input("Global Tx cost (bps)", min_value=0.0, value=0.0, step=0.1)
    txn_costs = global_cost

vol_targeting = st.sidebar.checkbox("Apply Volatility Targeting")
vol_target = None
vol_rebal_freq = None
if vol_targeting:
    vol_target = st.sidebar.number_input("Target Annual Volatility (%)", min_value=0.0, value=15.0, step=0.5) / 100
    vol_rebal_freq = st.sidebar.selectbox("Vol Rebalance Frequency", options=['Monthly','Quarterly','Yearly'], index=0)

hedge_spot = st.sidebar.checkbox("Equity Market Hedge (Short)")
hedge_fx = st.sidebar.checkbox("FX Hedge (Currency)")

# Product wrapping
st.sidebar.header("4. Product Wrapping")
use_autocall = st.sidebar.checkbox("Autocallable")
autocall_barrier = st.sidebar.number_input("Autocall Barrier (%)", min_value=0.0, value=100.0) / 100
autocall_coupon = st.sidebar.number_input("Autocall Coupon (%)", min_value=0.0, value=5.0) / 100
use_swap = st.sidebar.checkbox("Equity Swap")
swap_rate = st.sidebar.number_input("Fixed Swap Rate (%)", min_value=0.0, value=2.0) / 100

# Backtesting period
st.sidebar.header("5. Backtest Period")
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# Run simulation
if st.sidebar.button("Run Simulation"):
    if not selected_indices:
        st.error("Please select at least one index.")
    else:
        # Prepare price data
        price_df = data_loader.merge_indices(selected_indices)
        # Select return type
        if ret_type != 'price':
            for idx in selected_indices:
                series = data_loader.get_price_series(idx, return_type=ret_type, risk_free=risk_free)
                price_df[idx] = series.reindex(price_df.index)
        # Build portfolio
        if weights is None:
            weights = [1.0 / len(selected_indices)] * len(selected_indices)
        portfolio = Portfolio(price_df, weights,
                              rebalance_freq=rebalance_freq,
                              txn_costs=txn_costs,
                              vol_target=vol_target, vol_rebalance_freq=vol_rebal_freq,
                              hedge_spot=hedge_spot, hedge_fx=hedge_fx)
        # Wrap in structured product if needed
        product = None
        if use_autocall:
            product = Autocallable(portfolio, barrier=autocall_barrier, coupon=autocall_coupon)
        elif use_swap:
            product = Swap(portfolio, fixed_rate=swap_rate)
        # Run backtest
        bt = Backtester(portfolio, product)
        try:
            results = bt.run(start_date, end_date)
        except Exception as e:
            st.error(f"Backtest error: {e}")
            results = None
        
        if results:
            port_values = results['Portfolio Values']
            # Display performance chart
            st.subheader("Portfolio Value Over Time")
            st.line_chart(port_values)
            # Key Metrics
            st.subheader("Performance Metrics")
            kpis = results['Metrics']
            # Assume no benchmark provided; skip info ratio
            st.write(pd.DataFrame.from_dict(kpis, orient='index', columns=['Value']))
            
            # Drawdown chart
            drawdowns = (port_values / port_values.cummax()) - 1
            st.subheader("Drawdown")
            st.area_chart(drawdowns)
            
            # Save to session
            sim_name = st.text_input("Save this simulation as:", value="Sim1")
            if st.button("Save Simulation"):
                config = {
                    'indices': selected_indices,
                    'weights': weights,
                    'rebalance': rebalance_freq,
                    'txn_costs': txn_costs,
                    'vol_target': vol_target,
                    'hedge_spot': hedge_spot,
                    'hedge_fx': hedge_fx,
                    'product': 'Autocall' if use_autocall else 'Swap' if use_swap else None
                }
                save_simulation(sim_name, config, results)
                st.success(f"Simulation '{sim_name}' saved.")

# Load saved simulation
if 'saved_sims' in st.session_state:
    st.sidebar.header("Load Saved Simulation")
    sim_names = list(st.session_state['saved_sims'].keys())
    sel_sim = st.sidebar.selectbox("Select Simulation", sim_names)
    if st.sidebar.button("Load"):
        sim = load_simulation(sel_sim)
        if sim:
            res = sim['result']
            st.subheader(f"Loaded Simulation: {sel_sim}")
            st.line_chart(res['Portfolio Values'])
            metrics_df = pd.DataFrame.from_dict(res['Metrics'], orient='index', columns=['Value'])
            st.write(metrics_df)
