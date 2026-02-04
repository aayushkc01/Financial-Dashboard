from bokeh.io import curdoc
from bokeh.layouts import column, row, gridplot
from bokeh.models import (
    TextInput, Select, Button, Div, 
    RadioButtonGroup, Slider, CheckboxGroup, 
    PreText, HoverTool, CrosshairTool, Span, Label,
    Range1d
)
from bokeh.plotting import figure
from bokeh.themes import Theme
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# -----------------------
# Professional Themes
# -----------------------

PRO_THEMES = {
    "light": Theme(json={
        "attrs": {
            "Plot": {
                "background_fill_color": "#ffffff",
                "border_fill_color": "#ffffff",
                "outline_line_color": "#e0e0e0",
                "outline_line_width": 1,
            },
            "Axis": {
                "axis_line_color": "#666666",
                "axis_line_width": 1,
                "axis_label_text_color": "#333333",
                "axis_label_text_font_style": "normal",
                "major_label_text_color": "#555555",
                "major_tick_line_color": "#666666",
                "minor_tick_line_color": "#999999"
            },
            "Grid": {
                "grid_line_color": "#f0f0f0",
                "grid_line_alpha": 0.8,
                "grid_line_width": 0.5
            },
            "Title": {
                "text_color": "#2c3e50",
                "text_font_size": "16px",
                "text_font_style": "bold"
            },
            "Legend": {
                "background_fill_color": "#ffffff",
                "background_fill_alpha": 0.9,
                "label_text_color": "#333333",
                "border_line_color": "#e0e0e0",
                "border_line_width": 1,
                "border_line_alpha": 0.8
            }
        }
    }),
    
    "dark": Theme(json={
        "attrs": {
            "Plot": {
                "background_fill_color": "#1a1a2e",
                "border_fill_color": "#1a1a2e",
                "outline_line_color": "#2d3047",
                "outline_line_width": 1,
            },
            "Axis": {
                "axis_line_color": "#4a4e69",
                "axis_line_width": 1,
                "axis_label_text_color": "#e0e0e0",
                "axis_label_text_font_style": "normal",
                "major_label_text_color": "#b0b0b0",
                "major_tick_line_color": "#4a4e69",
                "minor_tick_line_color": "#3a3e59"
            },
            "Grid": {
                "grid_line_color": "#2d3047",
                "grid_line_alpha": 0.6,
                "grid_line_width": 0.5
            },
            "Title": {
                "text_color": "#ffffff",
                "text_font_size": "16px",
                "text_font_style": "bold"
            },
            "Legend": {
                "background_fill_color": "#16213e",
                "background_fill_alpha": 0.9,
                "label_text_color": "#e0e0e0",
                "border_line_color": "#2d3047",
                "border_line_width": 1,
                "border_line_alpha": 0.8
            }
        }
    }),
    
    "terminal": Theme(json={
        "attrs": {
            "Plot": {
                "background_fill_color": "#0c0c0c",
                "border_fill_color": "#0c0c0c",
                "outline_line_color": "#00ff00",
                "outline_line_width": 1,
            },
            "Axis": {
                "axis_line_color": "#00ff00",
                "axis_line_width": 1,
                "axis_label_text_color": "#00ff00",
                "axis_label_text_font_style": "normal",
                "major_label_text_color": "#00ff00",
                "major_tick_line_color": "#00ff00",
                "minor_tick_line_color": "#008800"
            },
            "Grid": {
                "grid_line_color": "#003300",
                "grid_line_alpha": 0.5,
                "grid_line_width": 0.5
            },
            "Title": {
                "text_color": "#00ff00",
                "text_font_size": "16px",
                "text_font_style": "bold"
            },
            "Legend": {
                "background_fill_color": "#0c0c0c",
                "background_fill_alpha": 0.9,
                "label_text_color": "#00ff00",
                "border_line_color": "#00ff00",
                "border_line_width": 1,
                "border_line_alpha": 0.8
            }
        }
    })
}

# Current theme and settings
current_theme = "light"

# Theme colors - COMPLETE FOR ALL THEMES
THEME_COLORS = {
    "light": {
        "bg": "#ffffff",
        "text": "#2c3e50", 
        "grid": "#f0f0f0",
        "up": "#2ecc71",
        "down": "#e74c3c",
        "widget_bg": "#f8f9fa"
    },
    "dark": {
        "bg": "#1a1a2e",
        "text": "#e0e0e0",
        "grid": "#2d3047",
        "up": "#27ae60",
        "down": "#c0392b",
        "widget_bg": "#2d3047"
    },
    "terminal": {
        "bg": "#0c0c0c",
        "text": "#00ff00",
        "grid": "#003300",  # ADDED MISSING KEY
        "up": "#00ff00",
        "down": "#ff0000",
        "widget_bg": "#1a1a1a"
    }
}

# -----------------------
# Financial Calculations
# -----------------------

def calculate_technical_indicators(df):
    """Calculate technical indicators"""
    if df is None or df.empty:
        return df
    
    # Basic indicators
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    return df

# -----------------------
# Plotting Functions
# -----------------------

def create_main_chart(df, indicators, theme):
    """Create main price chart"""
    colors = THEME_COLORS.get(theme, THEME_COLORS["light"])
    
    p = figure(
        x_axis_type="datetime",
        title=f"{current_ticker} - Price Chart",
        height=400,
        sizing_mode="stretch_width",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        background_fill_color=colors["bg"],
        border_fill_color=colors["bg"],
        toolbar_location="above",
        toolbar_sticky=False
    )
    
    # Professional styling
    p.title.text_font_size = "16pt"
    p.title.text_font_style = "bold"
    p.title.align = "center"
    p.title.text_color = colors["text"]
    
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Price (USD)"
    p.xaxis.axis_label_text_font_style = "bold"
    p.yaxis.axis_label_text_font_style = "bold"
    
    p.xaxis.major_label_text_color = colors["text"]
    p.yaxis.major_label_text_color = colors["text"]
    p.xaxis.axis_label_text_color = colors["text"]
    p.yaxis.axis_label_text_color = colors["text"]
    p.xaxis.axis_line_color = colors["text"]
    p.yaxis.axis_line_color = colors["text"]
    
    p.grid.grid_line_color = colors["grid"]
    p.grid.grid_line_alpha = 0.3
    
    # Add hover tool
    hover = HoverTool(
        tooltips=[
            ("Date", "@Date{%F}"),
            ("Open", "@Open{0,0.00}"),
            ("High", "@High{0,0.00}"),
            ("Low", "@Low{0,0.00}"),
            ("Close", "@Close{0,0.00}"),
            ("Volume", "@Volume{0,0}")
        ],
        formatters={"@Date": "datetime"},
        mode='vline'
    )
    p.add_tools(hover)
    
    # Add crosshair
    crosshair = CrosshairTool(dimensions="both", line_alpha=0.3)
    p.add_tools(crosshair)
    
    # Plot price line
    price_color = "#2E86AB" if theme in ["light", "terminal"] else "#4ECDC4"
    p.line(df['Date'], df['Close'], line_width=3, 
           color=price_color, alpha=0.8, legend_label="Close Price")
    
    # Add technical indicators
    if 'SMA/EMA' in indicators:
        p.line(df['Date'], df['SMA_20'], line_width=2, 
               color="#FF6B6B", alpha=0.7, legend_label="SMA 20")
        p.line(df['Date'], df['EMA_12'], line_width=2, 
               color="#F18F01", alpha=0.7, legend_label="EMA 12")
    
    if 'Bollinger Bands' in indicators and all(col in df.columns for col in ['BB_Upper', 'BB_Lower']):
        band_x = np.append(df['Date'].values, df['Date'].values[::-1])
        band_y = np.append(df['BB_Upper'].values, df['BB_Lower'].values[::-1])
        p.patch(band_x, band_y, color="#2E86AB", alpha=0.1, legend_label="Bollinger Band")
        p.line(df['Date'], df['BB_Upper'], line_width=1, color="#2E86AB", alpha=0.5)
        p.line(df['Date'], df['BB_Lower'], line_width=1, color="#2E86AB", alpha=0.5)
    
    # Add current price line
    if len(df) > 0:
        last_price = df['Close'].iloc[-1]
        price_line = Span(location=last_price, dimension='width', 
                          line_color='#FF6B6B', line_width=1, line_dash='dashed')
        p.add_layout(price_line)
        
        # Add price label
        price_label = Label(x=df['Date'].iloc[-1], y=last_price, 
                            text=f'${last_price:.2f}', 
                            text_color='#FF6B6B', text_font_size='10pt',
                            x_offset=10, y_offset=5)
        p.add_layout(price_label)
    
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    p.legend.background_fill_color = colors["widget_bg"]
    p.legend.label_text_color = colors["text"]
    p.legend.border_line_color = colors["grid"]
    p.legend.background_fill_alpha = 0.8
    p.legend.border_line_alpha = 0.5
    
    return p

def create_volume_chart(df, theme, x_range=None):
    """Create volume chart"""
    colors = THEME_COLORS.get(theme, THEME_COLORS["light"])
    
    # Color bars based on price movement
    if 'Open' in df.columns and 'Close' in df.columns:
        df['Color'] = np.where(df['Close'] >= df['Open'], colors["up"], colors["down"])
    else:
        df['Color'] = colors["up"]
    
    # Create figure
    p = figure(
        x_axis_type="datetime",
        height=150,
        sizing_mode="stretch_width",
        tools="",
        background_fill_color=colors["bg"],
        border_fill_color=colors["bg"]
    )
    
    # Set x_range if provided
    if x_range is not None:
        p.x_range = x_range
    
    p.vbar(x=df['Date'], top=df['Volume'], width=timedelta(days=0.8),
           color=df['Color'], alpha=0.7)
    
    p.yaxis.axis_label = "Volume"
    p.xaxis.axis_label = None
    
    # Style
    p.grid.grid_line_color = colors["grid"]
    p.grid.grid_line_alpha = 0.2
    p.yaxis.major_label_text_color = colors["text"]
    p.yaxis.axis_label_text_color = colors["text"]
    p.yaxis.axis_line_color = colors["text"]
    
    return p

def create_technical_chart(df, indicator_type, theme, x_range=None):
    """Create technical indicator sub-charts"""
    colors = THEME_COLORS.get(theme, THEME_COLORS["light"])
    
    p = figure(
        x_axis_type="datetime",
        height=200,
        sizing_mode="stretch_width",
        tools="",
        background_fill_color=colors["bg"],
        border_fill_color=colors["bg"]
    )
    
    # Set x_range if provided
    if x_range is not None:
        p.x_range = x_range
    
    if indicator_type == "RSI" and 'RSI' in df.columns:
        p.line(df['Date'], df['RSI'], line_width=2, color="#9b59b6")
        
        # Add RSI bands
        p.line(df['Date'], [70]*len(df), line_color="red", line_dash="dashed", line_width=1)
        p.line(df['Date'], [30]*len(df), line_color="green", line_dash="dashed", line_width=1)
        
        p.yaxis.axis_label = "RSI"
        p.y_range = Range1d(0, 100)
    
    elif indicator_type == "MACD" and all(col in df.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
        p.line(df['Date'], df['MACD'], line_width=2, color="#3498db", legend_label="MACD")
        p.line(df['Date'], df['MACD_Signal'], line_width=2, color="#e74c3c", legend_label="Signal")
        
        # Histogram
        colors_hist = np.where(df['MACD_Histogram'] >= 0, "#2ecc71", "#e74c3c")
        p.vbar(x=df['Date'], top=df['MACD_Histogram'], width=timedelta(days=0.6),
               color=colors_hist, alpha=0.6)
        
        p.yaxis.axis_label = "MACD"
        p.legend.location = "top_left"
    
    else:
        # Create empty chart with label
        p.yaxis.axis_label = indicator_type
    
    # Style
    p.grid.grid_line_color = colors["grid"]
    p.grid.grid_line_alpha = 0.2
    p.yaxis.major_label_text_color = colors["text"]
    p.yaxis.axis_label_text_color = colors["text"]
    p.xaxis.major_label_text_color = colors["text"]
    p.yaxis.axis_line_color = colors["text"]
    p.xaxis.axis_line_color = colors["text"]
    
    return p

# -----------------------
# Dashboard Components
# -----------------------

# Header
header = Div(text="""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; margin-bottom: 20px;">
    <h1 style="margin: 0; font-size: 32px; font-weight: 300;">
        <span style="font-weight: 600;">FINANCE</span> DASHBOARD
    </h1>
    <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">
        Professional Financial Analysis Platform
    </p>
</div>
""")

# Theme selector
theme_selector = RadioButtonGroup(
    labels=["🌞 Light", "🌙 Dark", "💻 Terminal"],
    active=0,
    button_type="success",
    width=300
)

# Ticker input
ticker_input = TextInput(
    title="📈 Ticker Symbol",
    value="AAPL",
    width=200,
    placeholder="e.g., AAPL, TSLA, GOOGL"
)

# Timeframe selector
timeframe = Select(
    title="⏰ Timeframe",
    value="3mo",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    width=200
)

# Indicator selector
indicator_groups = CheckboxGroup(
    labels=["SMA/EMA", "Bollinger Bands", "RSI", "MACD"],
    active=[0, 1],
    width=200
)

# Action buttons
run_analysis = Button(label="▶️ Run Analysis", button_type="primary", width=200, height=40)
export_data = Button(label="📥 Export Data", button_type="default", width=95)
refresh_data = Button(label="🔄 Refresh", button_type="success", width=95)

# Status panel
status_panel = PreText(text="Ready for analysis...", 
                      width=300, height=100, 
                      styles={"background-color": "#f8f9fa", 
                             "border": "1px solid #dee2e6",
                             "padding": "10px",
                             "border-radius": "5px",
                             "font-family": "monospace",
                             "font-size": "12px"})

# Stats display
stats_display = Div(text="", width=300)

# Dashboard container
dashboard_container = column(sizing_mode="stretch_both")

# -----------------------
# Callbacks and Logic
# -----------------------

current_ticker = "AAPL"
current_data = None

def update_theme(attr, old, new):
    """Update application theme"""
    global current_theme
    themes = ["light", "dark", "terminal"]
    current_theme = themes[new]
    curdoc().theme = PRO_THEMES[current_theme]
    update_status(f"Theme changed to {current_theme.capitalize()} Mode", "info")
    
    # Update widget styles
    update_widget_styles()

def update_widget_styles():
    """Update widget colors based on theme"""
    colors = THEME_COLORS.get(current_theme, THEME_COLORS["light"])
    
    # Update control section background
    controls_section.styles = {
        "background-color": colors["widget_bg"],
        "padding": "20px",
        "border-right": f"1px solid {colors['grid']}",
        "box-shadow": "2px 0 5px rgba(0,0,0,0.1)"
    }

def update_status(message, level="info"):
    """Update status panel"""
    colors = {
        "info": "blue",
        "success": "green",
        "warning": "orange",
        "error": "red"
    }
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    new_line = f"[{timestamp}] {message}"
    
    # Keep last 8 lines
    lines = status_panel.text.split('\n')
    if len(lines) > 8:
        lines = lines[-7:]
    
    status_panel.text = '\n'.join(lines + [new_line])
    
    # Update style for error/success
    if level == "error":
        status_panel.styles = {
            **status_panel.styles,
            "border-color": "#dc3545",
            "color": "#dc3545"
        }
    elif level == "success":
        status_panel.styles = {
            **status_panel.styles,
            "border-color": "#28a745",
            "color": "#28a745"
        }

def analyze_stock():
    """Main analysis function"""
    global current_ticker, current_data
    
    ticker = ticker_input.value.strip().upper()
    if not ticker:
        update_status("Please enter a valid ticker symbol", "error")
        return
    
    update_status(f"Loading data for {ticker}...", "info")
    
    try:
        # Load data
        df = yf.download(ticker, period=timeframe.value, progress=False)
        
        if df.empty:
            update_status(f"No data found for {ticker}", "error")
            return
        
        # Process data
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        df.reset_index(inplace=True)
        df["Date"] = pd.to_datetime(df["Date"])
        
        # Calculate indicators
        df = calculate_technical_indicators(df)
        current_data = df
        current_ticker = ticker
        
        # Create dashboard
        create_dashboard(df)
        
        # Update stats
        update_stats_display(df, ticker)
        
        update_status(f"Analysis complete for {ticker}", "success")
        
    except Exception as e:
        update_status(f"Error: {str(e)}", "error")
        print(f"Detailed error: {e}")

def create_dashboard(df):
    """Create comprehensive dashboard"""
    dashboard_container.children.clear()
    
    # Get selected indicators
    selected_indicators = []
    active_labels = [indicator_groups.labels[i] for i in indicator_groups.active]
    
    # Create main chart
    main_chart = create_main_chart(df, active_labels, current_theme)
    
    # Create volume chart
    volume_chart = create_volume_chart(df, current_theme, main_chart.x_range)
    
    # Create technical charts
    tech_charts = []
    if "RSI" in active_labels:
        tech_charts.append(create_technical_chart(df, "RSI", current_theme, main_chart.x_range))
    if "MACD" in active_labels:
        tech_charts.append(create_technical_chart(df, "MACD", current_theme, main_chart.x_range))
    
    # Arrange all charts
    all_charts = [main_chart, volume_chart] + tech_charts
    grid = gridplot(all_charts, ncols=1, sizing_mode="stretch_width", 
                   merge_tools=True, toolbar_location="above")
    
    dashboard_container.children.append(grid)

def update_stats_display(df, ticker):
    """Update statistics display"""
    if df is None or df.empty:
        return
    
    latest = df.iloc[-1]
    colors = THEME_COLORS.get(current_theme, THEME_COLORS["light"])
    
    if len(df) > 1:
        price_change = ((latest['Close'] - df.iloc[-2]['Close']) / df.iloc[-2]['Close']) * 100
    else:
        price_change = 0
    
    price_color = "#28a745" if price_change >= 0 else "#dc3545"
    
    stats_html = f"""
    <div style="background: {colors['widget_bg']}; 
                padding: 15px; border-radius: 8px; border: 1px solid {colors['grid']};">
        <h4 style="margin-top: 0; color: {colors['text']};">📊 {ticker} Statistics</h4>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div>
                <strong style="color: {colors['text']};">Current Price:</strong><br>
                <span style="font-size: 24px; font-weight: bold; color:{colors['text']}">
                    ${latest['Close']:.2f}
                </span><br>
                <span style="color: {price_color}; font-weight: bold;">
                    {price_change:+.2f}%
                </span>
            </div>
            
            <div>
                <strong style="color: {colors['text']};">Today's Range:</strong><br>
                <span style="color: {colors['text']}">
                    ${latest.get('Low', latest['Close']):.2f} - ${latest.get('High', latest['Close']):.2f}
                </span><br>
                <small style="color: {colors['text']}">Open: ${latest.get('Open', latest['Close']):.2f}</small>
            </div>
            
            <div>
                <strong style="color: {colors['text']};">Volume:</strong><br>
                <span style="color: {colors['text']}">
                    {latest.get('Volume', 0):,}
                </span><br>
                <small style="color: {colors['text']}">Avg: {df['Volume'].mean():,.0f}</small>
            </div>
            
            <div>
                <strong style="color: {colors['text']};">RSI (14):</strong><br>
                <span style="color: {colors['text']}">
                    {latest.get('RSI', 'N/A'):.1f if isinstance(latest.get('RSI'), (int, float)) else 'N/A'}
                </span><br>
                <small style="color: {colors['text']}">
    """
    
    rsi_value = latest.get('RSI')
    if isinstance(rsi_value, (int, float)):
        if rsi_value > 70:
            stats_html += "Overbought"
        elif rsi_value < 30:
            stats_html += "Oversold"
        else:
            stats_html += "Neutral"
    else:
        stats_html += "N/A"
    
    stats_html += f"""
                </small>
            </div>
        </div>
        
        <div style="margin-top: 10px; font-size: 12px; color: {colors['text']}; opacity: 0.7;">
            Data as of {latest['Date'].strftime('%Y-%m-%d')}
        </div>
    </div>
    """
    
    stats_display.text = stats_html

def export_to_csv():
    if current_data is not None:
        filename = f"{current_ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        current_data.to_csv(filename, index=False)
        update_status(f"Data exported to {filename}", "success")

def refresh_current():
    if current_ticker:
        analyze_stock()

# Connect callbacks
theme_selector.on_change('active', update_theme)
run_analysis.on_click(lambda: analyze_stock())
export_data.on_click(export_to_csv)
refresh_data.on_click(refresh_current)

# -----------------------
# Dashboard Layout
# -----------------------

# Left sidebar - Controls
controls_section = column(
    Div(text="<h3 style='color: #2c3e50; margin-bottom: 10px;'>⚙️ Settings</h3>"),
    theme_selector,
    
    Div(text="<h3 style='color: #2c3e50; margin-top: 20px; margin-bottom: 10px;'>📈 Data Input</h3>"),
    ticker_input,
    timeframe,
    
    Div(text="<h3 style='color: #2c3e50; margin-top: 20px; margin-bottom: 10px;'>📊 Indicators</h3>"),
    indicator_groups,
    
    Div(text="<h3 style='color: #2c3e50; margin-top: 20px; margin-bottom: 10px;'>🛠️ Actions</h3>"),
    run_analysis,
    row(export_data, refresh_data),
    
    Div(text="<h3 style='color: #2c3e50; margin-top: 20px; margin-bottom: 10px;'>📋 Statistics</h3>"),
    stats_display,
    
    Div(text="<h3 style='color: #2c3e50; margin-top: 20px; margin-bottom: 10px;'>📝 Log</h3>"),
    status_panel,
    
    width=350,
    sizing_mode="fixed"
)

# Main content area
main_content = column(
    dashboard_container,
    sizing_mode="stretch_both",
    styles={"padding": "20px", "background-color": "#fafafa"}
)

# Overall layout
layout = column(
    header,
    row(
        controls_section,
        main_content,
        sizing_mode="stretch_both"
    ),
    sizing_mode="stretch_both"
)

# Initialize
curdoc().theme = PRO_THEMES["light"]
curdoc().add_root(layout)
curdoc().title = "Finance Dashboard"

# Auto-run initial analysis
def initial_analysis():
    analyze_stock()

curdoc().add_next_tick_callback(initial_analysis)
