import numpy as np
import streamlit as st
import yfinance as yf
import mplfinance as mpf
import pandas as pd
import io
import base64
from features.data import GetData

st.set_page_config(layout="wide")
st.title('HotChick++  🚀🧑‍🚀')

import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def add_metrics_table_to_plot(fig, table_data):
    table_text = '\n'.join([f"{row[0]}: {row[1]}" for row in table_data[1:]])
    fig.text(0.11, 0.96, table_text, horizontalalignment='left', verticalalignment='top', fontsize=12, color='gray')


def create_chart(ticker, period, chart_type='light'):
    data = yf.download(ticker + '.NS', period=period)
    data = data.resample('B').ffill()

    data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
    data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
    data['VolMA10'] = data['Volume'].rolling(window=10).mean()

    if chart_type == 'volume_candles':
        fig, ax = plt.subplots(figsize=(18, 8))

        relative_volume = data['Volume'] / data['Volume'].max()
        min_width = 0.5
        max_width = 2
        widths = min_width + (max_width - min_width) * relative_volume

        up = data['Close'] > data['Open']
        down = data['Close'] <= data['Open']

        ax.bar(data.index[up], data['High'][up] - data['Low'][up], bottom=data['Low'][up],
               width=widths[up], color='g', align='center', alpha=0.8)
        ax.bar(data.index[up], data['Close'][up] - data['Open'][up], bottom=data['Open'][up],
               width=widths[up], color='g', align='center')

        ax.bar(data.index[down], data['High'][down] - data['Low'][down], bottom=data['Low'][down],
               width=widths[down], color='r', align='center', alpha=0.8)
        ax.bar(data.index[down], data['Open'][down] - data['Close'][down], bottom=data['Close'][down],
               width=widths[down], color='r', align='center')

        ax.plot(data.index, data['EMA50'], color='orange', linewidth=1, label='EMA50')
        ax.plot(data.index, data['EMA200'], color='purple', linewidth=1, label='EMA200')

        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title(f'{ticker} - Volume Candles')
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.6)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)

        plt.tight_layout()
    else:
        import mplfinance as mpf

        mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', gridcolor='gray', rc={'font.size': 8})

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
            style = mpf.make_mpf_style(
                base_mpl_style='dark_background', marketcolors=dark_mc,
                figcolor='black', gridstyle=':', gridcolor='dimgrey',
                rc={'axes.labelcolor': 'white', 'axes.edgecolor': 'white',
                    'xtick.color': 'white', 'ytick.color': 'white',
                    'axes.facecolor': 'black', 'figure.facecolor': 'black',
                    'savefig.facecolor': 'black', 'savefig.edgecolor': 'black'}
            )
        else:
            style = s

        fig, _ = mpf.plot(
            data, type='candle', style=style, title=f'\n{ticker}',
            figsize=(18, 8), volume=True, panel_ratios=(3, 1), tight_layout=True,
            addplot=addplots, returnfig=True
        )
        table_data = get_analysis(data)
        add_metrics_table_to_plot(fig, table_data)

    return fig


# get lefft analytics
def get_analysis(data):
    data['r-vol'] = data['Volume'].rolling(window=10).mean().pct_change(periods=40)
    data['ATR'] = calculate_atr(data)
    data['Turnover'] = data['Volume'] * data['Close']
    data['AvgTurnover10'] = data['Turnover'].rolling(window=2).mean()
    data['TurnoverCategory'] = np.where(data['AvgTurnover10'] >= 10000000, 'high', 'low')
    dict = get_metrics_table(data)
    return dict


def get_metrics_table(data):
    latest_data = data.iloc[-1]
    avg_turnover_lakh = (latest_data['AvgTurnover10'] / 10000000)
    table_data = [
        ['Metric', 'Value'],
        ['r-vol', f"{latest_data['r-vol']:.2%}"],
        ['ATR', f"{latest_data['ATR']:.2f}"],
        ['max investment', f"{latest_data['TurnoverCategory']} ₹ ({avg_turnover_lakh:,.2f} lakh)"]
    ]
    return table_data


def calculate_atr(data, period=3):
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()


def get_image_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def to_excel(df1, df2, df3):
    # Create a BytesIO buffer
    buffer = io.BytesIO()

    # Write dataframes to the buffer
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name='sandpile', index=False)
        df2.to_excel(writer, sheet_name='darvas', index=False)
        df3.to_excel(writer, sheet_name='20 Pips', index=False)
        writer.close()  # Close the writer to finalize the buffer content

    # Get the content of the buffer
    excel_data = buffer.getvalue()
    return excel_data


# Define the available scans
scans = {"sandpile": 1, '20 Pips': 2, 'darvas': 3}
scan_type = st.selectbox("Select scan type", options=list(scans.keys()), )


@st.cache_data
def load_tickers(scan_type):
    scan_db = GetData()
    df1, df2, df3 = scan_db.get_piles()

    # Add extra columns to each dataframe
    def add_empty_columns(df):
        df['Pattern'] = ""
        df['Volume'] = ""
        df['ShareHolding'] = ""
        df['Watchlist'] = ""
        return df

    df1 = add_empty_columns(df1)
    df2 = add_empty_columns(df2)
    df3 = add_empty_columns(df3)

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


if st.button('Download as Excel'):
    # Get dataframes for all types
    df1, df2, df3 = load_tickers("sandpile")[0], load_tickers("darvas")[0], load_tickers("20 Pips")[0]

    # Generate Excel file
    excel_data = to_excel(df1, df2, df3)

    # Provide download link
    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name='tickers.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

tickers_df, strat_counts = load_tickers(scan_type)
st.table(strat_counts)

# Streamlit app

# Session state to keep track of current ticker index
if 'ticker_index' not in st.session_state:
    st.session_state.ticker_index = 0


# Function to move to the next stock
def next_stock():
    st.session_state.ticker_index = (st.session_state.ticker_index + 1) % len(tickers_df)


chart_type = {"light": 'light', 'dark': 'dark', 'volume_candles': 'volume_candles'}
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
    elif chart_type_b == 'volume_candles':
        fig = create_chart(current_ticker, date_ranges[selected_range], chart_type='volume_candles')

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

st.markdown("r-vol: rolling volume\n pct_change(10day avg volume, 2 min) ")
