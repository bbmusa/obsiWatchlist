import streamlit as st
import yfinance as yf
import mplfinance as mpf
import pandas as pd
import io
import base64
from features.data import GetData

st.set_page_config(layout="wide")
st.title('HotChick++  🚀🧑‍🚀')


def create_chart(ticker, period, chart_type='light'):
    # Download historical data
    data = yf.download(ticker + '.NS', period=period)
    data = data.resample('B').ffill()  # Resample and fill forward

    # Calculate indicators
    data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
    data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
    data['VolMA10'] = data['Volume'].rolling(window=10).mean()

    # Define market colors
    mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', gridcolor='gray', rc={'font.size': 8})

    # Define addplots for EMA and Volume MA
    addplots = [
        mpf.make_addplot(data['EMA50'], color='orange', width=1),
        mpf.make_addplot(data['EMA200'], color='purple', width=1),
        mpf.make_addplot(data['VolMA10'], panel=1, color='red', width=1)
    ]

    if chart_type == 'dark':
        dark_mc = mpf.make_marketcolors(
            up='lime', down='red', wick={'up': 'lime', 'down': 'red'},
            edge={'up': 'lime', 'down': 'red'}, volume={'up': 'lime', 'down': 'red'}
        )
        dark_style = mpf.make_mpf_style(
            base_mpl_style='dark_background', marketcolors=dark_mc,
            figcolor='black',
            rc={'axes.labelcolor': 'white', 'axes.edgecolor': 'white',
                'xtick.color': 'white', 'ytick.color': 'white',
                'axes.facecolor': 'black', 'figure.facecolor': 'black',
                'savefig.facecolor': 'black', 'savefig.edgecolor': 'black'}
        )

        # Plot candlestick chart with volume bars in dark theme
        fig, _ = mpf.plot(
            data, type='candle', style=dark_style, title=f'\n{ticker}',
            figsize=(18, 8), volume=True, panel_ratios=(3, 1), tight_layout=True,
            addplot=addplots, returnfig=True
        )
    else:
        # Plot candlestick chart with volume
        fig, _ = mpf.plot(
            data, type='candle', style=s, title=f'\n{ticker}',
            figsize=(18, 8), volume=True, panel_ratios=(3, 1), tight_layout=True,
            addplot=addplots, returnfig=True
        )
    return fig


# Function to get image as base64
def get_image_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


# Define the available scans
scans = {"sandpile": 1, '20 Pips': 2, 'darvas': 3}
scan_type = st.selectbox("Select scan type", options=list(scans.keys()), )


@st.cache_data
def load_tickers(scan_type):
    scan_db = GetData()
    df1, df2, df3 = scan_db.get_piles()
    if scan_type == "sandpile":
        df = df1
    elif scan_type == "20 Pips":
        df = df3
    elif scan_type == "darvas":
        df = df2
    counts = pd.DataFrame({
        'Type': ['sandpile', '20 Pips', 'darvas'],
        'Count': [len(df1), len(df3), len(df2)]
    })
    return df, counts


tickers_df, strat_counts = load_tickers(scan_type)
st.table(strat_counts)

# Streamlit app

# Session state to keep track of current ticker index
if 'ticker_index' not in st.session_state:
    st.session_state.ticker_index = 0


# Function to move to the next stock
def next_stock():
    st.session_state.ticker_index = (st.session_state.ticker_index + 1) % len(tickers_df)


chart_type = {"light": 'light', 'dark': 'dark'}
chart_type_b = st.selectbox("Select chart type", options=list(chart_type.keys()), )

# Date range buttons
date_ranges = {'3m': '3mo', '6m': '6mo', '1y': '1y', '5y': '5y'}
selected_range = st.radio("Select Date Range", list(date_ranges.keys()), horizontal=True)

# Display current stock and chart
current_ticker = tickers_df.iloc[st.session_state.ticker_index]['nsecode']
st.subheader(f"Current Stock: {current_ticker}")

try:
    if chart_type_b == 'light':
        fig = create_chart(current_ticker, date_ranges[selected_range])
    else:
        fig = create_chart(current_ticker, date_ranges[selected_range], chart_type='dark')
    img_base64 = get_image_base64(fig)
    st.markdown(f'<img src="data:image/png;base64,{img_base64}" style="width: 100%;">', unsafe_allow_html=True)
except Exception as e:
    st.error(f"Error loading data for {current_ticker}: {str(e)}")

# Next stock button
if st.button("Next Stock"):
    next_stock()

# JavaScript to handle spacebar press
st.markdown("""
<script>
document.addEventListener('keydown', function(e) {
    if (e.keyCode == 32 && e.target == document.body) {
        e.preventDefault();
        document.querySelector('button[kind="secondary"]').click();
    }
});
</script>
""", unsafe_allow_html=True)

st.markdown("Press spacebar to move to the next stock.")
