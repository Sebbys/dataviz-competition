from flask import Flask, render_template, request, jsonify, flash
import pandas as pd
import os
import numpy as np
from bokeh.plotting import figure, show
from bokeh.embed import components
from bokeh.models import FactorRange, HoverTool, ColumnDataSource
from bokeh.palettes import Spectral6, Category20, Viridis6
from bokeh.transform import factor_cmap
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Load the dataset globally with error handling
try:
    df = pd.read_csv('data/Sustainable Development Goal 08 - Decent Work and Economic Growth data.csv')
    logger.info(f"Dataset loaded successfully with {len(df)} rows")
except FileNotFoundError:
    logger.error("Dataset file not found!")
    df = pd.DataFrame()  # Empty dataframe as fallback
except Exception as e:
    logger.error(f"Error loading dataset: {e}")
    df = pd.DataFrame()

# Enhanced categories with better organization and descriptions
CATEGORY_INDICATORS = {
    "economy": {
        "display_name": "💰 Economic Development",
        "description": "Key indicators measuring economic growth, financial inclusion, and trade performance",
        "color": "#3B82F6",
        "indicators": {
            "SL_EMP_EARN": "8.5.1 Average hourly earnings of employees",
            "DC_TOF_TRDCML": "8.1.1 Total official flows commitments for Aid for Trade",
            "DC_TOF_TRDDBML": "8.1.2 Total official flows disbursed for Aid for Trade",
            "FB_BNK_ACCSS": "8.10.1 Account at a financial institution or mobile-money-service provider",
        }
    },
    "work": {
        "display_name": "👥 Employment & Labor",
        "description": "Metrics related to employment rates, productivity, and youth engagement",
        "color": "#10B981",
        "indicators": {
            "NY_GDP_PCAP": "8.2.1 Annual growth rate of real GDP per employed person",
            "SL_TLF_UEM": "8.5.2 Unemployment rate, by sex, age and persons with disabilities",
            "SL_TLF_NEET": "8.6.1 Proportion of youth not in education, employment or training",
        }
    },
    "trade_resources": {
        "display_name": "🏝️ Trade & Tourism",
        "description": "Indicators focusing on tourism development and resource utilization",
        "color": "#F59E0B",
        "indicators": {
            "SL_TLF_CHD": "8.7.1 Proportion and number of children aged 5‑17 years engaged in child labour",
            "SPC_8_9_1": "8.9.1 Tourism direct GDP as a proportion of total GDP",
            "SPC_8_9_1IN": "8.9.1 Tourism direct GDP as a proportion of total GDP (inbound)",
        }
    },
    "social_growth": {
        "display_name": "🌱 Social Development",
        "description": "Social indicators measuring sustainable development and growth patterns",
        "color": "#8B5CF6",
        "indicators": {
            "SPC_8_9_1OUT": "8.9.1 Tourism direct GDP as a proportion of total GDP (outbound)",
        }
    }
}

def get_data_summary(data):
    """Get summary statistics for the dataset"""
    if data.empty:
        return {}
    
    return {
        'total_records': len(data),
        'countries': data['Pacific Island Countries and territories'].nunique() if 'Pacific Island Countries and territories' in data.columns else 0,
        'time_periods': data['TIME_PERIOD'].nunique() if 'TIME_PERIOD' in data.columns else 0,
        'indicators': data['INDICATOR'].nunique() if 'INDICATOR' in data.columns else 0
    }

def create_enhanced_bar_chart(data, indicator_display_name):
    """Create an enhanced bar chart with improved styling"""
    logger.info(f"Creating bar chart with {len(data)} data points")
    
    if data.empty:
        logger.warning("Data is empty for bar chart")
        return None, None
      # Clean and aggregate data
    data_clean = data.copy()
    
    # Handle missing values and clean data
    data_clean = data_clean.dropna(subset=['OBS_VALUE'])  # Remove rows with missing values
    data_clean = data_clean[data_clean['OBS_VALUE'] != '']  # Remove rows with empty strings
    
    # Convert OBS_VALUE to numeric, errors='coerce' will turn invalid values to NaN
    data_clean['OBS_VALUE'] = pd.to_numeric(data_clean['OBS_VALUE'], errors='coerce')
    data_clean = data_clean.dropna(subset=['OBS_VALUE'])  # Remove NaN values after conversion
    
    if data_clean.empty:
        logger.warning("No valid numeric data after cleaning")
        return None, None
    
    data_clean['Pacific Island Countries and territories'] = data_clean['Pacific Island Countries and territories'].astype(str).str.strip()
    aggregated_data = data_clean.groupby('Pacific Island Countries and territories')['OBS_VALUE'].mean().reset_index()
    aggregated_data = aggregated_data.rename(columns={'Pacific Island Countries and territories': 'country_territory'})
    aggregated_data = aggregated_data.sort_values('OBS_VALUE', ascending=False)
    aggregated_data = aggregated_data.dropna()
    
    logger.info(f"Aggregated data has {len(aggregated_data)} countries")
    logger.info(f"Countries: {aggregated_data['country_territory'].tolist()}")
    
    if aggregated_data.empty:
        logger.warning("Aggregated data is empty for bar chart")
        return None, None
      # Create the plot
    countries = aggregated_data['country_territory'].tolist()
    p = figure(
        x_range=countries,
        height=400, 
        sizing_mode='stretch_width',
        title=f'Statistical Analysis: {indicator_display_name}',
        x_axis_label="Country/Territory", 
        y_axis_label="Average Value",
        toolbar_location="above"
    )
    
    # Add bars with enhanced styling using simple colors
    colors = Spectral6 * (len(countries) // len(Spectral6) + 1)
    aggregated_data['colors'] = colors[:len(countries)]
    source = ColumnDataSource(aggregated_data)
    
    bars = p.vbar(
        x='country_territory', 
        top='OBS_VALUE', 
        width=0.8, 
        source=source,
        fill_color='colors',
        line_color="white",
        line_width=2,
        alpha=0.8
    )
    
    # Styling
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.xaxis.major_label_orientation = 45
    p.title.text_font_size = "14pt"
    p.title.align = "center"
    
    # Enhanced hover tool
    hover = HoverTool(tooltips=[
        ("Country/Territory", "@country_territory"),
        ("Average Value", "@OBS_VALUE{0.00}"),
        ("Indicator", indicator_display_name)
    ])
    p.add_tools(hover)
    
    return components(p)

def create_enhanced_box_plot(data, indicator_display_name):
    """Create an enhanced box plot with statistical insights using simple rectangles"""
    logger.info(f"Creating box plot with {len(data)} data points")
    
    if data.empty:
        logger.warning("Data is empty for box plot")
        return None, None
    
    # Clean data first
    data_clean = data.copy()
    data_clean = data_clean.dropna(subset=['OBS_VALUE'])  # Remove rows with missing values
    data_clean = data_clean[data_clean['OBS_VALUE'] != '']  # Remove rows with empty strings
    
    # Convert OBS_VALUE to numeric
    data_clean['OBS_VALUE'] = pd.to_numeric(data_clean['OBS_VALUE'], errors='coerce')
    data_clean = data_clean.dropna(subset=['OBS_VALUE'])  # Remove NaN values after conversion
    
    if data_clean.empty:
        logger.warning("No valid numeric data after cleaning for box plot")
        return None, None
        
    # Calculate box plot statistics
    box_data = data_clean.groupby('Pacific Island Countries and territories')['OBS_VALUE'].agg([
        ('q1', lambda x: x.quantile(0.25)),
        ('median', lambda x: x.quantile(0.5)),
        ('q3', lambda x: x.quantile(0.75)),
        ('mean', 'mean'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max')
    ]).reset_index()
    
    # Calculate whiskers (1.5 * IQR)
    box_data['iqr'] = box_data['q3'] - box_data['q1']
    box_data['upper'] = np.minimum(box_data['q3'] + 1.5 * box_data['iqr'], box_data['max'])
    box_data['lower'] = np.maximum(box_data['q1'] - 1.5 * box_data['iqr'], box_data['min'])
    
    box_data = box_data.rename(columns={'Pacific Island Countries and territories': 'country_territory'})
    box_data = box_data.sort_values('median', ascending=False)
    
    # Filter out any rows with NaN values
    box_data = box_data.dropna()
    
    if box_data.empty:
        return None, None
    
    countries = box_data['country_territory'].tolist()
    p = figure(
        x_range=countries, 
        height=400, 
        sizing_mode='stretch_width',
        title=f'Geographic Distribution: {indicator_display_name}',
        x_axis_label="Country/Territory", 
        y_axis_label="Value Distribution",
        toolbar_location="above"
    )
    
    source = ColumnDataSource(box_data)
    
    # Create box plot using simple rectangles and lines
    # Box (Q1 to Q3)
    p.rect(x='country_territory', y='median', width=0.6, height='iqr',
           fill_color=Viridis6[2], line_color="black", alpha=0.7, source=source)
    
    # Median line
    p.segment(x0='country_territory', y0='median', x1='country_territory', y1='median',
              line_width=3, line_color="white", source=source)
    
    # Whisker lines (vertical lines from Q1 to lower, Q3 to upper)
    p.segment(x0='country_territory', y0='q1', x1='country_territory', y1='lower',
              line_width=2, line_color="black", source=source)
    p.segment(x0='country_territory', y0='q3', x1='country_territory', y1='upper',
              line_width=2, line_color="black", source=source)
    
    # Whisker caps
    p.segment(x0='country_territory', y0='lower', x1='country_territory', y1='lower',
              line_width=8, line_color="black", source=source)
    p.segment(x0='country_territory', y0='upper', x1='country_territory', y1='upper',
              line_width=8, line_color="black", source=source)
    
    # Mean points
    p.circle(x='country_territory', y='mean', size=8, color="red", alpha=0.8, source=source)
    
    # Styling
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 45
    p.title.text_font_size = "14pt"
    p.title.align = "center"
    
    # Enhanced hover tool
    hover = HoverTool(tooltips=[
        ("Country/Territory", "@country_territory"),
        ("Median", "@median{0.00}"),
        ("Mean", "@mean{0.00}"),
        ("Q1", "@q1{0.00}"),
        ("Q3", "@q3{0.00}"),
        ("Min", "@min{0.00}"),
        ("Max", "@max{0.00}"),
        ("Std Dev", "@std{0.00}")
    ])
    p.add_tools(hover)
    
    return components(p)

def create_enhanced_line_chart(data, indicator_display_name):
    """Create an enhanced line chart with temporal analysis"""
    logger.info(f"Creating line chart with {len(data)} data points")
    
    if data.empty:
        logger.warning("Data is empty for line chart")
        return None, None
    
    # Clean data first
    data_clean = data.copy()
    data_clean = data_clean.dropna(subset=['OBS_VALUE'])  # Remove rows with missing values
    data_clean = data_clean[data_clean['OBS_VALUE'] != '']  # Remove rows with empty strings
    
    # Convert OBS_VALUE to numeric
    data_clean['OBS_VALUE'] = pd.to_numeric(data_clean['OBS_VALUE'], errors='coerce')
    data_clean = data_clean.dropna(subset=['OBS_VALUE'])  # Remove NaN values after conversion
    
    if data_clean.empty:
        logger.warning("No valid numeric data after cleaning for line chart")
        return None, None
        
    # Prepare data
    data_clean['TIME_PERIOD'] = data_clean['TIME_PERIOD'].astype(str)
    time_periods = sorted(data_clean['TIME_PERIOD'].unique())
    
    p = figure(
        height=400, 
        sizing_mode='stretch_width',
        title=f'Temporal Trends: {indicator_display_name}',
        x_axis_label="Time Period", 
        y_axis_label="Value",
        toolbar_location="above"
    )
    
    # Set x_range manually to avoid FactorRange issues
    p.x_range.range_padding = 0.1
    
    # Color palette for countries
    countries = data_clean['Pacific Island Countries and territories'].unique()
    countries = [c for c in countries if pd.notna(c)]  # Filter out NaN values
    colors = Category20[min(len(countries), 20)]
    
    # Convert time periods to numeric for plotting
    time_period_map = {period: i for i, period in enumerate(time_periods)}
      # Plot line for each country
    for i, country in enumerate(countries):
        country_data = data_clean[data_clean['Pacific Island Countries and territories'] == country].copy()
        country_data = country_data.sort_values('TIME_PERIOD')
        country_data = country_data.dropna(subset=['OBS_VALUE'])
        
        if not country_data.empty and len(country_data) > 0:
            # Convert OBS_VALUE to numeric if not already done
            country_data['OBS_VALUE'] = pd.to_numeric(country_data['OBS_VALUE'], errors='coerce')
            country_data = country_data.dropna(subset=['OBS_VALUE'])
            
            if not country_data.empty:
                # Map time periods to numbers
                country_data['time_numeric'] = country_data['TIME_PERIOD'].map(time_period_map)
                source = ColumnDataSource(country_data)
                color = colors[i % len(colors)]
                
                # Add line and circles
                p.line(x='time_numeric', y='OBS_VALUE', source=source, 
                       legend_label=country, line_width=2, color=color, alpha=0.8)
                p.circle(x='time_numeric', y='OBS_VALUE', source=source, 
                         size=6, color=color, alpha=0.8)
    
    # Set x-axis labels
    p.xaxis.ticker = list(range(len(time_periods)))
    p.xaxis.major_label_overrides = {i: period for i, period in enumerate(time_periods)}
    
    # Styling
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 45
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    p.title.text_font_size = "14pt"
    p.title.align = "center"
    
    # Enhanced hover tool
    hover = HoverTool(tooltips=[
        ("Country", "@{Pacific Island Countries and territories}"),
        ("Time Period", "@TIME_PERIOD"),
        ("Value", "@OBS_VALUE{0.00}")
    ])
    p.add_tools(hover)
    
    return components(p)
    
    # Styling
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 45
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    p.title.text_font_size = "14pt"
    p.title.align = "center"
    
    # Enhanced hover tool
    hover = HoverTool(tooltips=[
        ("Country", "@{Pacific Island Countries and territories}"),
        ("Time Period", "@TIME_PERIOD"),
        ("Value", "@OBS_VALUE{0.00}")
    ])
    p.add_tools(hover)
    
    return components(p)

# Ensure the visualization directory exists
if not os.path.exists('static/visualizations'):
    os.makedirs('static/visualizations')

@app.route('/')
def index():
    """Homepage route with enhanced data summary"""
    data_summary = get_data_summary(df)
    
    return render_template(
        'index.html',
        title="Pacific Economy Data Visualization Dashboard",
        categories_data=CATEGORY_INDICATORS,
        selected_category_key="economy",
        selected_indicator_code="",
        data_summary=data_summary,
        bokeh_script_bar=None, bokeh_div_bar=None,
        bokeh_script_box=None, bokeh_div_box=None,
        bokeh_script_line=None, bokeh_div_line=None
    )

@app.route('/api/indicators/<category>')
def get_indicators(category):
    """API endpoint to get indicators for a category"""
    try:
        if category in CATEGORY_INDICATORS:
            return jsonify(CATEGORY_INDICATORS[category]['indicators'])
        else:
            return jsonify({}), 404
    except Exception as e:
        logger.error(f"Error getting indicators for category {category}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/visualize', methods=['POST'])
def visualize():
    """Enhanced visualization route with better error handling"""
    try:
        selected_category_key = request.form.get('category', '').strip()
        indicator_code = request.form.get('indicator', '').strip()

        # Validation
        if not selected_category_key or not indicator_code:
            flash('Please select both a category and an indicator.', 'error')
            return render_template('index.html', 
                                 title="Pacific Economy Data Visualization Dashboard",
                                 categories_data=CATEGORY_INDICATORS,
                                 selected_category_key=selected_category_key,
                                 selected_indicator_code="",
                                 data_summary=get_data_summary(df),
                                 bokeh_script_bar=None, bokeh_div_bar=None,
                                 bokeh_script_box=None, bokeh_div_box=None,
                                 bokeh_script_line=None, bokeh_div_line=None)

        if selected_category_key not in CATEGORY_INDICATORS:
            flash('Invalid category selected.', 'error')
            return render_template('index.html', 
                                 title="Pacific Economy Data Visualization Dashboard",
                                 categories_data=CATEGORY_INDICATORS,
                                 selected_category_key="economy",
                                 selected_indicator_code="",
                                 data_summary=get_data_summary(df),
                                 bokeh_script_bar=None, bokeh_div_bar=None,
                                 bokeh_script_box=None, bokeh_div_box=None,
                                 bokeh_script_line=None, bokeh_div_line=None)

        # Get indicator display name
        indicators = CATEGORY_INDICATORS.get(selected_category_key, {}).get("indicators", {})
        indicator_display_name = indicators.get(indicator_code, indicator_code)

        # Filter data
        filtered_data = df[df['INDICATOR'] == indicator_code] if not df.empty else pd.DataFrame()
        
        if filtered_data.empty:
            flash(f'No data found for the selected indicator: {indicator_display_name}', 'warning')
            return render_template('index.html', 
                                 title="Pacific Economy Data Visualization Dashboard",
                                 categories_data=CATEGORY_INDICATORS,
                                 selected_category_key=selected_category_key,
                                 selected_indicator_code=indicator_code,
                                 selected_indicator_display_name=indicator_display_name,
                                 data_summary=get_data_summary(df),
                                 bokeh_script_bar=None, bokeh_div_bar=None,
                                 bokeh_script_box=None, bokeh_div_box=None,
                                 bokeh_script_line=None, bokeh_div_line=None)

        logger.info(f"Generating visualizations for {indicator_display_name} with {len(filtered_data)} records")

        # Generate enhanced visualizations
        bokeh_script_bar, bokeh_div_bar = create_enhanced_bar_chart(filtered_data, indicator_display_name)
        bokeh_script_box, bokeh_div_box = create_enhanced_box_plot(filtered_data, indicator_display_name)
        bokeh_script_line, bokeh_div_line = create_enhanced_line_chart(filtered_data, indicator_display_name)

        # Flash success message
        flash(f'Visualizations generated successfully for: {indicator_display_name}', 'success')

        return render_template('index.html', 
                             title="Pacific Economy Data Visualization Dashboard",
                             categories_data=CATEGORY_INDICATORS,
                             selected_category_key=selected_category_key,
                             selected_indicator_code=indicator_code,
                             selected_indicator_display_name=indicator_display_name,
                             data_summary=get_data_summary(filtered_data),
                             bokeh_script_bar=bokeh_script_bar, bokeh_div_bar=bokeh_div_bar,
                             bokeh_script_box=bokeh_script_box, bokeh_div_box=bokeh_div_box,
                             bokeh_script_line=bokeh_script_line, bokeh_div_line=bokeh_div_line)

    except Exception as e:
        logger.error(f"Error in visualize route: {e}")
        flash('An error occurred while generating visualizations. Please try again.', 'error')
        return render_template('index.html', 
                             title="Pacific Economy Data Visualization Dashboard",
                             categories_data=CATEGORY_INDICATORS,
                             selected_category_key="economy",
                             selected_indicator_code="",
                             data_summary=get_data_summary(df),
                             bokeh_script_bar=None, bokeh_div_bar=None,
                             bokeh_script_box=None, bokeh_div_box=None,
                             bokeh_script_line=None, bokeh_div_line=None)

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error handler"""
    return render_template('index.html', 
                         title="Pacific Economy Data Visualization Dashboard",
                         categories_data=CATEGORY_INDICATORS,
                         selected_category_key="economy",
                         selected_indicator_code="",
                         data_summary=get_data_summary(df),
                         bokeh_script_bar=None, bokeh_div_bar=None,
                         bokeh_script_box=None, bokeh_div_box=None,
                         bokeh_script_line=None, bokeh_div_line=None), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Custom 500 error handler"""
    logger.error(f"Internal server error: {e}")
    flash('An internal server error occurred. Please try again later.', 'error')
    return render_template('index.html', 
                         title="Pacific Economy Data Visualization Dashboard",
                         categories_data=CATEGORY_INDICATORS,
                         selected_category_key="economy",
                         selected_indicator_code="",
                         data_summary=get_data_summary(df),
                         bokeh_script_bar=None, bokeh_div_bar=None,
                         bokeh_script_box=None, bokeh_div_box=None,
                         bokeh_script_line=None, bokeh_div_line=None), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    
    logger.info(f"Starting Flask application on port {port}")
    logger.info(f"Debug mode: {debug_mode}")
    logger.info(f"Dataset status: {'Loaded' if not df.empty else 'Empty/Failed to load'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
