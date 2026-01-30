from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (
    TextInput, Select, MultiSelect, Button, Div
)
from bokeh.plotting import figure
import yfinance as yf
import pandas as pd

# -----------------------
# Helpers
# -----------------------

def load_data(ticker, period):
    try:
        df = yf.download(ticker, period=period, progress=False)

        if df.empty:
            return None

        # 🔥 FIX: flatten multi-index columns
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        df.reset_index(inplace=True)
        
        # 🔥 CRITICAL FIX: Ensure Date column is datetime
        df["Date"] = pd.to_datetime(df["Date"])
        
        return df

    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def price_plot(df, indicators, title):
    # Create plot with specific sizing
    p = figure(
        x_axis_type="datetime",
        title=title,
        height=400,
        width=800,
        sizing_mode="stretch_both",
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )

    # Ensure we have valid data
    if df is not None and not df.empty and "Date" in df.columns and "Close" in df.columns:
        p.line(df["Date"], df["Close"], line_width=2, legend_label="Close", color="blue")

        if "SMA" in indicators:
            df["SMA"] = df["Close"].rolling(window=20).mean()
            p.line(df["Date"], df["SMA"], color="orange", line_width=2, legend_label="SMA 20")

        if "EMA" in indicators:
            df["EMA"] = df["Close"].ewm(span=20, adjust=False).mean()
            p.line(df["Date"], df["EMA"], color="green", line_width=2, legend_label="EMA 20")

        p.legend.location = "top_left"
        p.legend.click_policy = "hide"
        
        # Format axes
        p.xaxis.axis_label = "Date"
        p.yaxis.axis_label = "Price (USD)"
        
    return p


# -----------------------
# Widgets
# -----------------------

ticker_input = TextInput(title="Ticker Symbol", value="AAPL", width=200)

timeframe = Select(
    title="Timeframe",
    value="6mo",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    width=200
)

indicators = MultiSelect(
    title="Indicators",
    value=["SMA"],
    options=["SMA", "EMA"],
    size=2,
    width=200
)

run_button = Button(label="Run Analysis", button_type="success", width=200)

status = Div(
    text="Enter a ticker and click Run Analysis",
    styles={"color": "#555", "font-size": "14px", "width": "280px"}
)

plot_container = column(sizing_mode="stretch_both")

# -----------------------
# Callback
# -----------------------

def on_button_click():
    plot_container.children.clear()

    ticker = ticker_input.value.strip().upper()
    
    if not ticker:
        status.text = "❌ Please enter a ticker symbol"
        status.styles = {"color": "red", "font-weight": "bold"}
        return
    
    status.text = f"⏳ Loading data for {ticker}..."
    status.styles = {"color": "orange", "font-weight": "bold"}
    
    df = load_data(ticker, timeframe.value)

    if df is None or df.empty:
        status.text = f"❌ No data found for {ticker}"
        status.styles = {"color": "red", "font-weight": "bold"}
        return
    
    if "Date" not in df.columns or "Close" not in df.columns:
        status.text = f"❌ Invalid data structure for {ticker}"
        status.styles = {"color": "red", "font-weight": "bold"}
        print(f"Columns available: {df.columns.tolist()}")
        return

    status.text = f"✅ Loaded {len(df)} days of data for {ticker}"
    status.styles = {"color": "green", "font-weight": "bold"}

    p = price_plot(df, indicators.value, f"{ticker} Price Chart")
    plot_container.children.append(p)
    
    # Debug info
    print(f"Data loaded for {ticker}:")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"Close price range: {df['Close'].min():.2f} to {df['Close'].max():.2f}")
    print(f"Indicators selected: {indicators.value}")


run_button.on_click(on_button_click)

# -----------------------
# Layout
# -----------------------

controls = column(
    Div(text="<h2>Financial Dashboard</h2>", styles={"text-align": "center"}),
    ticker_input,
    timeframe,
    indicators,
    run_button,
    status,
    width=300,
    sizing_mode="fixed"
)

layout = row(
    controls, 
    plot_container, 
    sizing_mode="stretch_both",
    margin=10,
    spacing=20
)

curdoc().add_root(layout)
curdoc().title = "Financial Dashboard"
