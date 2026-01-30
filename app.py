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
        df.reset_index(inplace=True)
        return df
    except Exception:
        return None


def price_plot(df, indicators, title):
    p = figure(
        x_axis_type="datetime",
        title=title,
        height=350,
        sizing_mode="stretch_width",
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )

    p.line(df["Date"], df["Close"], line_width=2, legend_label="Close")

    if "SMA" in indicators:
        df["SMA"] = df["Close"].rolling(20).mean()
        p.line(df["Date"], df["SMA"], color="orange", legend_label="SMA 20")

    if "EMA" in indicators:
        df["EMA"] = df["Close"].ewm(span=20).mean()
        p.line(df["Date"], df["EMA"], color="green", legend_label="EMA 20")

    p.legend.location = "top_left"
    return p


# -----------------------
# Widgets
# -----------------------

ticker_input = TextInput(title="Ticker Symbol", value="AAPL")

timeframe = Select(
    title="Timeframe",
    value="6mo",
    options=["1mo", "3mo", "6mo", "1y", "2y"]
)

indicators = MultiSelect(
    title="Indicators",
    value=["SMA"],
    options=["SMA", "EMA"]
)

run_button = Button(label="Run Analysis", button_type="success")

status = Div(
    text="Enter a ticker and click Run Analysis",
    styles={"color": "#555", "font-size": "14px"}
)

plot_container = column()

# -----------------------
# Callback
# -----------------------

def on_button_click():
    plot_container.children.clear()

    ticker = ticker_input.value.strip().upper()
    df = load_data(ticker, timeframe.value)

    if df is None:
        status.text = f"❌ No data found for {ticker}"
        status.styles = {"color": "red", "font-weight": "bold"}
        return

    status.text = f"✅ Loaded data for {ticker}"
    status.styles = {"color": "green", "font-weight": "bold"}

    p = price_plot(df, indicators.value, f"{ticker} Price Chart")
    plot_container.children.append(p)


run_button.on_click(on_button_click)

# -----------------------
# Layout
# -----------------------

controls = column(
    ticker_input,
    timeframe,
    indicators,
    run_button,
    status,
    width=300
)

layout = row(controls, plot_container, sizing_mode="stretch_width")

curdoc().add_root(layout)
curdoc().title = "Financial Dashboard"
