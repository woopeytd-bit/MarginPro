import streamlit as st
import requests

# Page Config
st.set_page_config(page_title="CAD Margin Pro", page_icon="🇨🇦", layout="centered")

# App Header
st.title("🇨🇦 CAD Margin Pro")
st.markdown("### Professional Margin & Currency Dashboard")

# 1. Fetch Live Data (Cached for performance)
@st.cache_data(ttl=3600) # Refresh rates every hour
def get_fx_rates():
    try:
        response = requests.get("https://api.frankfurter.dev/v1/latest?base=CAD")
        return response.json().get("rates", {})
    except:
        return {}

rates = get_fx_rates()

# 2. Sidebar Configuration
st.sidebar.header("Settings")
mode = st.sidebar.radio("Calculation Goal", ["Find Selling Price", "Find Margin %"])
tax_rate = st.sidebar.number_input("Tax / HST (%)", value=13.0, step=1.0)
target_currency = st.sidebar.selectbox("Convert Result To", ["USD", "EUR", "GBP", "JPY", "AUD", "MXN"])

# 3. Main Input Section
col1, col2 = st.columns(2)

with col1:
    cost = st.number_input("Cost (CAD, Excl. Tax)", min_value=0.01, value=100.00, step=1.0)

with col2:
    if mode == "Find Selling Price":
        margin_input = st.number_input("Target Margin (%)", min_value=1.0, max_value=99.0, value=30.0)
    else:
        price_input = st.number_input("Sale Price (CAD, Excl. Tax)", min_value=0.01, value=142.86)

# 4. Calculation Logic
if mode == "Find Selling Price":
    sell_price = cost / (1 - (margin_input / 100))
    margin_val = margin_input
else:
    sell_price = price_input
    margin_val = ((sell_price - cost) / sell_price) * 100

profit = sell_price - cost
markup = (profit / cost) * 100
total_with_tax = sell_price * (1 + (tax_rate / 100))

# 5. Display Results
st.divider()

# Metric Row
m1, m2, m3 = st.columns(3)

# Using :.2f inside f-strings for clean currency formatting
m1.metric("Selling Price (CAD)", f"${sell_price:,.2f}")
m2.metric("Margin", f"{margin_val:.1f}%")

# The delta shows the Markup percentage as a sub-text
m3.metric("Profit", f"${profit:,.2f}", delta=f"{markup:.1f}% Markup")

st.divider()

# Localization & Tax Card
with st.expander("View Tax & Currency Breakdown", expanded=True):
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("**Tax Details**")
        st.write(f"Price with {tax_rate}% Tax: **${total_with_tax:,.2f}**")
        st.write(f"Tax Amount: `${(total_with_tax - sell_price):,.2f}`")

    with c2:
        # Safely fetch the rate; default to 1.0 if not found
        current_rate = rates.get(target_currency, 1.0)
        st.write(f"**FX Conversion (1 CAD = {current_rate:.4f} {target_currency})**")
        
        converted_price = sell_price * current_rate
        st.write(f"Price in {target_currency}: **{converted_price:,.2f} {target_currency}**")
