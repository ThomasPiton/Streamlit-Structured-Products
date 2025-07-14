import streamlit as st
import pandas as pd
from api.yahoo_finance import YahooFinance
from src.compute.level_index import LevelIndex
from datetime import date, timedelta
from src.utils import get_last_business_day
from src.displayer.display_factory import DisplayFactory

st.title("Index Structuration Simulation")
st.markdown("Use this application to simulate and price you structured product")

params = {}

today = date.today()
start_of_year = date(today.year, 1, 1)
last_business_day = get_last_business_day(today)

st.header("1. Custom Basket Builder")

# Number of components
nb_components = st.number_input("Number of Components", min_value=1, max_value=20, value=5, step=1)
params["nb_components"] = nb_components



# Hide index in DataFrame-like layout
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    div[data-testid="stHorizontalBlock"] > div {
        margin-bottom: -0.5rem;  /* reduce vertical space between rows */
    }
    .stNumberInput, .stTextInput {
        padding-top: 0rem;
        padding-bottom: 0rem;
        margin-bottom: 0rem;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("##### Component Weights Table")

components = []

default_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
default_weights = [20.0, 20.0, 20.0, 20.0, 20.0]

# Table headers
header_cols = st.columns([2, 1])
header_cols[0].markdown("**Ticker**")
header_cols[1].markdown("**Weight (%)**")

# Table rows with dynamic input
for i in range(nb_components):
    cols = st.columns([2, 1])

    with cols[0]:
        ticker = st.text_input(
            label=f"Ticker {i+1}",
            label_visibility="collapsed",
            value=default_tickers[i] if i < len(default_tickers) else "",
            key=f"ticker_{i}"
        )
    with cols[1]:
        weight = st.number_input(
            label=f"Weight {i+1}",
            label_visibility="collapsed",
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            value=default_weights[i] if i < len(default_weights) else 0.0,
            key=f"weight_{i}"
        )

    components.append({"ticker": ticker, "weight": weight})

params["components"] = components

# Sum weights
total_weight = sum(row["weight"] for row in components)

# Display weight sum and alerts
st.markdown(f"**Total Weight: {total_weight:.2f}%**")
if total_weight > 100:
    st.error("⚠️ Total weight exceeds 100%!")
elif total_weight < 100:
    st.warning("ℹ️ Total weight is below 100%. Consider adjusting.")
else:
    st.success("✅ Total weight is exactly 100%.")

use_rebalancing = st.checkbox("Enable Rebalancing")

if use_rebalancing:
    rebalancing_freq = st.selectbox("Rebalancing Frequency",["Daily", "Weekly", "Monthly", "Quarterly"])
    transaction_cost = st.number_input("Transaction Cost (%)", min_value=0.0, max_value=100.0, value=0.05, step=0.01)
    params.update({"rebalancing_freq":rebalancing_freq,"transaction_cost":transaction_cost})

return_type = st.selectbox(
    "Return Type Methodology",
    ["Price Return","Excess Return", "Total Return", "Net Total Return", "Gross Return", "Synthetic Dividend Total Return"]
)

params["return_type"] = return_type

if return_type == "Excess Return":
    excess_return_benchmark = st.selectbox(
        "Select Benchmark for Excess Return",
        ["^SOFR", "^IRX", "^EURSTRON"],
        help="Used to compute return relative to this benchmark (e.g., cash or risk-free rate)"
    )
    params["excess_return_benchmark"] = excess_return_benchmark

elif return_type == "Total Return":
    st.info("Includes both price appreciation and dividends reinvested.")

elif return_type == "Net Total Return":
    withholding_rate = st.number_input(
        "Withholding Tax Rate on Dividends (%)",
        min_value=0.0,
        max_value=100.0,
        value=15.0,
        step=0.1,
        help="Net of dividend tax (typically 15%-30% depending on jurisdiction)"
    )
    params["withholding_rate"] = withholding_rate

elif return_type == "Gross Return":
    st.info("Gross total return assumes no tax withholding on dividends.")

elif return_type == "Synthetic Dividend Total Return":
    synthetic_dividend_level = st.number_input(
        "Synthetic Dividend Level (%)",
        min_value=0.0,
        max_value=20.0,
        value=2.0,
        step=0.1,
        help="Assumes a synthetic dividend stream at a fixed level"
    )
    params["synthetic_dividend_level"] = synthetic_dividend_level

index_currency = st.selectbox("Index Currency", ["EUR", "USD"])
params["index_currency"] = index_currency

use_vol_target = st.checkbox("Enable Volatility Target")

if use_vol_target:
    target_vol = st.number_input("Target Volatility Level (%)", min_value=0.1, max_value=100.0, value=10.0, step=0.1)
    vol_window = st.number_input("Volatility Estimation Window (days)", min_value=1, max_value=500, value=60, step=1)
    vol_method = st.selectbox("Computation Methodology", ["Historical", "Exponential"])
    params.update({"target_vol":target_vol,"vol_window":vol_window,"vol_method":vol_method})


st.header("2. Custom Wrapper Configuration")

wrapper = st.selectbox("Wrapper", ["Note", "Swap","ETF","Fund"])
params["wrapper"] = wrapper

if wrapper == "Note":
    st.markdown("### Note Parameters")
    autocall_barrier = st.number_input("Autocall Barrier (%)", min_value=0.0, max_value=200.0, step=0.5)
    redemption_barrier = st.number_input("Redemption Barrier (%)", min_value=0.0, max_value=200.0, step=0.5)
    coupon = st.number_input("Coupon (%)", min_value=0.0, step=0.1)
    maturity_years = st.number_input("Duration (Years)", min_value=0.0, step=0.5)
    observation_frequency = st.selectbox("Observation Frequency", ["Monthly", "Quarterly", "Annually"])
    effet_memoire = st.checkbox("Memory Effect")
    barrier_type = st.selectbox("Barrier Type", ["European", "American", "Continuous"])
    option_type = st.selectbox("Option Type", ["Worst of", "Best of", "Single Underlying"])
    capital_guaranteed = st.checkbox("Capital Guaranteed?")
    st.date_input("Observation Dates", key="observation_dates", help="Select key observation dates manually")
    fx_hedged = st.checkbox("FX Hedged")
    
    params.update(
        {
            "autocall_barrier":autocall_barrier,
            "redemption_barrier":redemption_barrier,
            "coupon":coupon,
            "maturity_years":maturity_years,
            "observation_frequency":observation_frequency,
            "effet_memoire":effet_memoire,
            "barrier_type":barrier_type,
            "option_type":option_type,
            "capital_guaranteed":capital_guaranteed,
            "fx_hedged":fx_hedged,
        }
    )

elif wrapper == "ETF":
    st.markdown("### ETF Parameters")
    distributing = st.radio("Distributing or Accumulating?", ["Distributing", "Accumulating"])
    fx_hedged = st.checkbox("FX Hedged")
    
    params.update(
        {
            "distributing":distributing,
            "fx_hedged":fx_hedged,
        }
    )

elif wrapper == "Swap":
    st.markdown("### Swap Parameters")
    payer_leg = st.text_input("Payer Leg Description")
    fixed_rate = st.number_input("Fixed Rate (%)", min_value=0.0, step=0.01)
    receiver_leg = st.text_input("Receiver Leg Description")
    floating_rate_index = st.selectbox("Floating Rate Index", ["SOFR", "EURIBOR", "LIBOR", "ESTR"])
    fx_hedged = st.checkbox("FX Hedged")
    
    params.update(
        {
            "payer_leg":payer_leg,
            "fixed_rate":fixed_rate,
            "receiver_leg":receiver_leg,
            "floating_rate_index":floating_rate_index,
            "fx_hedged":fx_hedged,
        }
    )

elif wrapper == "Fund":
    st.markdown("### Fund Parameters")
    entry_fee = st.number_input("Entry Fee (%)", min_value=0.0, step=0.01)
    exit_fee = st.number_input("Exit Fee (%)", min_value=0.0, step=0.01)
    management_fee = st.number_input("Management Fee (%)", min_value=0.0, step=0.01)
    performance_fee = st.number_input("Performance Fee (%)", min_value=0.0, step=0.01)
    fx_hedged = st.checkbox("FX Hedged")
    
    params.update(
        {
            "entry_fee":entry_fee,
            "exit_fee":exit_fee,
            "management_fee":management_fee,
            "performance_fee":performance_fee,
            "fx_hedged":fx_hedged,
        }
    )

st.header("3. Client Setting")

client_notional = st.number_input("Notional (€)", min_value=0.0, step=1000.0, format="%.2f")
client_maturity = st.date_input("Maturity Date", format="YYYY-MM-DD")

client_name = st.text_input("Client Name")
client_type = st.selectbox("Client Type", ["Individual", "Institution", "Wealth Manager"])
client_country = st.selectbox("Client Country", ["France", "Germany", "USA", "UK", "Other"])
client_currency = st.selectbox("Currency Preference", ["EUR", "USD", "GBP", "JPY"])
risk_profile = st.selectbox("Risk Appetite", ["Conservative", "Balanced", "Aggressive"])
liquidity_needs = st.selectbox("Liquidity Needs", ["High", "Medium", "Low"])
expected_return = st.number_input("Expected Return (%)", min_value=0.0, max_value=100.0, step=0.1)
max_drawdown = st.number_input("Max Drawdown Tolerance (%)", min_value=0.0, max_value=100.0, step=0.1)
restrictions = st.text_area("Mandate Restrictions", placeholder="List any constraints (e.g., no leverage, no derivatives)...")
ucits_eligible = st.checkbox("UCITS Eligible?")
tax_sensitive = st.checkbox("Tax Sensitive?")

params.update(
        {
            "client_notional":client_notional,
            "client_maturity":client_maturity,
            "client_name":client_name,
            "client_type":client_type,
            "client_country":client_country,
            "client_currency":client_currency,
            "risk_profile":risk_profile,
            "liquidity_needs":liquidity_needs,
            "expected_return":expected_return,
            "max_drawdown":max_drawdown,
            "restrictions":restrictions,
            "ucits_eligible":ucits_eligible,
            "tax_sensitive":tax_sensitive
        }
    )

st.header("4. Backtest setting")

benchmark_ticker = st.text_input("Benchmark Ticker (e.g. ^GSPC, ^STOXX50E)", value="^GSPC")
index_launch_date = st.date_input("Index Launch Date")
act_method = st.selectbox("Calendar Day Count Convention", ["Actual/Actual", "30/360", "Actual/360", "Actual/365"])
start_date = st.date_input("Backtest Start Date",value=start_of_year)
end_date = st.date_input("Backtest End Date",value=last_business_day)
live_start = st.date_input("Live Period Start Date (optional)",help="Used for split reporting")
initial_amount = st.number_input("Initial Notional (€)", min_value=0, step=1, value=1000000)

params.update(
        {
            "benchmark_ticker":benchmark_ticker,
            "index_launch_date":index_launch_date,
            "act_method":act_method,
            "start_date":start_date,
            "end_date":end_date,
            "live_start":live_start,
            "initial_amount":initial_amount
        }
    )

st.markdown("---")

if st.button("Compute Simulation"):
    data_forex = YahooFinance(**params).get_currency()
    data = YahooFinance(**params).get_data()
    level_index = LevelIndex(data=data, params=params).compute()
    
    DisplayFactory(display="DISPLAY_TEST_V1", index=level_index).render()