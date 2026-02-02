from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (
    TextInput, Select, MultiSelect, Button, Div, 
    Toggle, ColorPicker, RadioButtonGroup
)
from bokeh.plotting import figure
from bokeh.themes import Theme
import yfinance as yf
import pandas as pd

# -----------------------
# Themes
# -----------------------

DARK_THEME = Theme(json={
    "attrs": {
        "Plot": {
            "background_fill_color": "#1e1e1e",
            "border_fill_color": "#1e1e1e",
            "outline_line_color": "#444444",
        },
        "Axis": {
            "axis_line_color": "#666666",
            "axis_label_text_color": "#cccccc",
            "major_label_text_color": "#aaaaaa",
            "major_tick_line_color": "#666666",
            "minor_tick_line_color": "#444444"
        },
        "Grid": {
            "grid_line_color": "#333333",
            "grid_line_alpha": 0.5
        },
        "Title": {
            "text_color": "#ffffff"
        },
        "Legend": {
            "background_fill_color": "#2e2e2e",
            "label_text_color": "#cccccc",
            "border_line_color": "#444444"
        }
    }
})

LIGHT_THEME = Theme(json={
    "attrs": {
        "Plot": {
            "background_fill_color": "#ffffff",
            "border_fill_color": "#ffffff",
            "outline_line_color": "#cccccc",
        },
        "Axis": {
            "axis_line_color": "#666666",
            "axis_label_text_color": "#333333",
            "major_label_text_color": "#555555",
            "major_tick_line_color": "#666666",
            "minor_tick_line_color": "#999999"
        },
        "Grid": {
            "grid_line_color": "#e0e0e0",
            "grid_line_alpha": 0.8
        },
        "Title": {
            "text_color": "#333333"
        },
        "Legend": {
            "background_fill_color": "#f9f9f9",
            "label_text_color": "#333333",
            "border_line_color": "#cccccc"
        }
    }
})

# Current theme state
current_theme = "light"
theme_colors = {
    "light": {
        "background": "#ffffff",
        "text": "#333333",
        "secondary": "#666666",
        "widget_bg": "#f5f5f5",
        "border": "#dddddd"
    },
    "dark": {
        "background": "#1e1e1e",
        "text": "#ffffff",
        "secondary": "#cccccc",
        "widget_bg": "#2e2e2e",
        "border": "#444444"
    }
}

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


def create_plot(df, indicators, title, theme="light"):
    colors = theme_colors[theme]
    
    # Create plot with theme-specific colors
    p = figure(
        x_axis_type="datetime",
        title=title,
        height=400,
        width=800,
        sizing_mode="stretch_both",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        background_fill_color=colors["background"],
        border_fill_color=colors["background"]
    )
    
    # Style the plot based on theme
    p.title.text_color = colors["text"]
    p.xaxis.axis_label_text_color = colors["text"]
    p.yaxis.axis_label_text_color = colors["text"]
    p.xaxis.major_label_text_color = colors["secondary"]
    p.yaxis.major_label_text_color = colors["secondary"]
    p.xaxis.axis_line_color = colors["border"]
    p.yaxis.axis_line_color = colors["border"]
    p.xgrid.grid_line_color = colors["border"]
    p.ygrid.grid_line_color = colors["border"]
    p.xgrid.grid_line_alpha = 0.3
    p.ygrid.grid_line_alpha = 0.3

    # Ensure we have valid data
    if df is not None and not df.empty and "Date" in df.columns and "Close" in df.columns:
        # Line colors that work well in both themes
        line_colors = {
            "light": {"close": "#1f77b4", "sma": "#ff7f0e", "ema": "#2ca02c"},
            "dark": {"close": "#4dabf7", "sma": "#ffa94d", "ema": "#69db7c"}
        }
        
        theme_line_colors = line_colors[theme]
        
        p.line(df["Date"], df["Close"], line_width=2, 
               legend_label="Close", color=theme_line_colors["close"])

        if "SMA" in indicators:
            df["SMA"] = df["Close"].rolling(window=20).mean()
            p.line(df["Date"], df["SMA"], color=theme_line_colors["sma"], 
                   line_width=2, legend_label="SMA 20")

        if "EMA" in indicators:
            df["EMA"] = df["Close"].ewm(span=20, adjust=False).mean()
            p.line(df["Date"], df["EMA"], color=theme_line_colors["ema"], 
                   line_width=2, legend_label="EMA 20")

        # Style legend based on theme
        p.legend.location = "top_left"
        p.legend.click_policy = "hide"
        p.legend.background_fill_color = colors["widget_bg"]
        p.legend.label_text_color = colors["text"]
        p.legend.border_line_color = colors["border"]
        
        # Format axes
        p.xaxis.axis_label = "Date"
        p.yaxis.axis_label = "Price (USD)"
        
    return p


def update_widget_styles(theme):
    """Update widget styles based on theme"""
    colors = theme_colors[theme]
    
    # Update all widgets' styles
    ticker_input.styles = {
        "background-color": colors["widget_bg"],
        "color": colors["text"],
        "border-color": colors["border"]
    }
    
    timeframe.styles = {
        "background-color": colors["widget_bg"],
        "color": colors["text"],
        "border-color": colors["border"]
    }
    
    indicators.styles = {
        "background-color": colors["widget_bg"],
        "color": colors["text"],
        "border-color": colors["border"]
    }
    
    status.styles = {
        "color": colors["text"],
        "font-weight": "bold",
        "background-color": colors["widget_bg"],
        "padding": "5px",
        "border-radius": "3px"
    }
    
    # Update header
    header.styles = {
        "color": colors["text"],
        "text-align": "center",
        "margin-bottom": "20px"
    }


# -----------------------
# Widgets
# -----------------------

header = Div(text="<h1 style='margin-bottom: 5px;'>📈 Financial Dashboard</h1>", 
             styles={"text-align": "center", "margin-bottom": "20px"})

# Theme selector
theme_toggle = Toggle(label="🌙 Dark Mode", active=False, 
                      button_type="default", width=200)

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
    styles={"color": "#555", "font-size": "14px", "width": "280px", 
            "background-color": "#f5f5f5", "padding": "5px", "border-radius": "3px"}
)

plot_container = column(sizing_mode="stretch_both")

# -----------------------
# Callbacks
# -----------------------

def on_theme_toggle(attr, old, new):
    """Handle theme toggle"""
    global current_theme
    
    if new:  # Dark mode activated
        current_theme = "dark"
        theme_toggle.label = "☀️ Light Mode"
        curdoc().theme = DARK_THEME
    else:    # Light mode activated
        current_theme = "light"
        theme_toggle.label = "🌙 Dark Mode"
        curdoc().theme = LIGHT_THEME
    
    # Update widget styles
    update_widget_styles(current_theme)
    
    # If there's a plot, recreate it with new theme
    if hasattr(on_button_click, 'last_df') and hasattr(on_button_click, 'last_ticker'):
        recreate_plot_with_current_theme()


def recreate_plot_with_current_theme():
    """Recreate the current plot with the new theme"""
    if hasattr(on_button_click, 'last_df') and on_button_click.last_df is not None:
        plot_container.children.clear()
        
        p = create_plot(
            on_button_click.last_df, 
            indicators.value, 
            f"{on_button_click.last_ticker} Price Chart",
            current_theme
        )
        plot_container.children.append(p)


def on_button_click():
    plot_container.children.clear()

    ticker = ticker_input.value.strip().upper()
    
    if not ticker:
        status.text = "❌ Please enter a ticker symbol"
        status.styles = {"color": "red", "font-weight": "bold"}
        return
    
    status.text = f"⏳ Loading data for {ticker}..."
    
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
    
    # Store the data for theme changes
    on_button_click.last_df = df
    on_button_click.last_ticker = ticker
    
    p = create_plot(df, indicators.value, f"{ticker} Price Chart", current_theme)
    plot_container.children.append(p)
    
    # Debug info
    print(f"Data loaded for {ticker} in {current_theme} mode:")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"Close price range: {df['Close'].min():.2f} to {df['Close'].max():.2f}")
    print(f"Indicators selected: {indicators.value}")


# Initialize storage for theme switching
on_button_click.last_df = None
on_button_click.last_ticker = None

# Connect callbacks
run_button.on_click(on_button_click)
theme_toggle.on_change('active', on_theme_toggle)

# -----------------------
# Layout
# -----------------------

# Theme controls section
theme_section = column(
    Div(text="<h3>Theme Settings</h3>", styles={"margin-bottom": "10px"}),
    theme_toggle,
    width=300,
    styles={"background-color": "#f8f9fa", "padding": "15px", "border-radius": "5px", 
            "border": "1px solid #dee2e6"}
)

# Data controls section
data_section = column(
    Div(text="<h3>Chart Settings</h3>", styles={"margin-bottom": "10px"}),
    ticker_input,
    timeframe,
    indicators,
    run_button,
    status,
    width=300,
    styles={"background-color": "#f8f9fa", "padding": "15px", "border-radius": "5px", 
            "border": "1px solid #dee2e6", "margin-top": "20px"}
)

# Combine controls
controls = column(
    header,
    theme_section,
    data_section,
    width=320,
    sizing_mode="fixed"
)

layout = row(
    controls, 
    plot_container, 
    sizing_mode="stretch_both",
    margin=10,
    spacing=20
)

# Set initial theme
curdoc().theme = LIGHT_THEME
update_widget_styles(current_theme)
curdoc().add_root(layout)
curdoc().title = "Financial Dashboard"
