from flask import Flask, render_template, request, flash
import pandas as pd
import os
import logging
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.palettes import Category20

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Load dataset
def load_data():
    """Load the CSV data with proper error handling"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'data', 'Sustainable Development Goal 08 - Decent Work and Economic Growth data.csv')
        df = pd.read_csv(csv_path)
        logger.info(f"Dataset loaded successfully with {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        return pd.DataFrame()

# Global data loading
df = load_data()

# Categories and indicators configuration
CATEGORIES = {
    "economy": {
        "name": "💰 Economic Development",
        "indicators": {
            "SL_EMP_EARN": "Average hourly earnings of employees",
            "DC_TOF_TRDCML": "Aid for Trade commitments",
            "FB_BNK_ACCSS": "Financial institution access"
        }
    },
    "work": {
        "name": "👥 Employment & Labor", 
        "indicators": {
            "NY_GDP_PCAP": "GDP per employed person growth",
            "SL_TLF_UEM": "Unemployment rate",
            "SL_TLF_NEET": "Youth not in education/employment"
        }
    },
    "trade": {
        "name": "🚢 Trade & Resources",
        "indicators": {
            "DC_TOF_TRDDBML": "Aid for Trade disbursements",
            "SL_EMP_EARN": "Employment earnings"
        }
    }
}

def clean_data(data, indicator):
    """Clean and prepare data for visualization"""
    if data.empty:
        return pd.DataFrame()
    
    # Filter by indicator
    filtered = data[data['INDICATOR'] == indicator].copy()
    
    # Clean numeric values
    filtered['OBS_VALUE'] = pd.to_numeric(filtered['OBS_VALUE'], errors='coerce')
    filtered = filtered.dropna(subset=['OBS_VALUE'])
    
    return filtered

def create_bar_chart(data, title):
    """Create a simple bar chart"""
    if data.empty:
        return None, None
    
    try:
        # Group by country and get mean values
        country_data = data.groupby('REF_AREA')['OBS_VALUE'].mean().reset_index()
        country_data = country_data.sort_values('OBS_VALUE', ascending=False).head(10)
        
        # Create plot
        p = figure(
            x_range=country_data['REF_AREA'].tolist(),
            height=400,
            width=700,
            title=f"Bar Chart: {title}",
            toolbar_location="above"
        )
        
        # Add bars
        p.vbar(
            x=country_data['REF_AREA'],
            top=country_data['OBS_VALUE'],
            width=0.7,
            color='#3182ce',
            alpha=0.8
        )
        
        # Styling
        p.xaxis.major_label_orientation = 45
        p.xaxis.axis_label = "Country"
        p.yaxis.axis_label = "Value"
        
        # Add hover
        hover = HoverTool(tooltips=[("Country", "@x"), ("Value", "@top{0.00}")])
        p.add_tools(hover)
        
        return components(p)
    
    except Exception as e:
        logger.error(f"Error creating bar chart: {e}")
        return None, None

def create_box_plot(data, title):
    """Create a simple box plot visualization"""
    if data.empty:
        return None, None
        
    try:
        # Get statistics by country
        stats = data.groupby('REF_AREA')['OBS_VALUE'].agg(['min', 'max', 'mean', 'median']).reset_index()
        stats = stats.head(8)  # Limit to 8 countries for readability
        
        # Create plot
        p = figure(
            x_range=stats['REF_AREA'].tolist(),
            height=400,
            width=700,
            title=f"Box Plot: {title}",
            toolbar_location="above"
        )
        
        # Add simple box representation using rectangles
        for i, row in stats.iterrows():
            country = row['REF_AREA']
            mean_val = row['mean']
            min_val = row['min']
            max_val = row['max']
            median_val = row['median']
            
            # Box (from min to max)
            p.rect(x=country, y=(min_val + max_val) / 2, width=0.5, height=max_val - min_val, 
                   color='lightblue', alpha=0.6)
            
            # Median line
            p.line(x=[country, country], y=[median_val, median_val], line_width=3, color='red')
        
        p.xaxis.major_label_orientation = 45
        p.xaxis.axis_label = "Country"
        p.yaxis.axis_label = "Value"
        
        return components(p)
        
    except Exception as e:
        logger.error(f"Error creating box plot: {e}")
        return None, None

def create_line_chart(data, title):
    """Create a simple line chart"""
    if data.empty:
        return None, None
        
    try:
        # Check if we have time period data
        if 'TIME_PERIOD' not in data.columns:
            # Use REF_AREA as x-axis if no time data
            country_data = data.groupby('REF_AREA')['OBS_VALUE'].mean().reset_index()
            country_data = country_data.sort_values('OBS_VALUE').head(10)
            
            p = figure(
                height=400,
                width=700,
                title=f"Line Chart: {title}",
                toolbar_location="above"
            )
            
            p.line(x=range(len(country_data)), y=country_data['OBS_VALUE'], 
                   line_width=2, color='#10b981')
            p.circle(x=range(len(country_data)), y=country_data['OBS_VALUE'], 
                     size=8, color='#10b981')
            
            p.xaxis.ticker = list(range(len(country_data)))
            p.xaxis.major_label_overrides = {i: country for i, country in enumerate(country_data['REF_AREA'])}
            
        else:
            # Use time-based data
            time_data = data.groupby('TIME_PERIOD')['OBS_VALUE'].mean().reset_index()
            time_data = time_data.sort_values('TIME_PERIOD')
            
            p = figure(
                height=400,
                width=700,
                title=f"Line Chart: {title}",
                toolbar_location="above"
            )
            
            p.line(x=time_data['TIME_PERIOD'], y=time_data['OBS_VALUE'], 
                   line_width=2, color='#10b981')
            p.circle(x=time_data['TIME_PERIOD'], y=time_data['OBS_VALUE'], 
                     size=8, color='#10b981')
        
        p.xaxis.major_label_orientation = 45
        p.xaxis.axis_label = "Period/Country"
        p.yaxis.axis_label = "Value"
        
        # Add hover
        hover = HoverTool(tooltips=[("X", "@x"), ("Value", "@y{0.00}")])
        p.add_tools(hover)
        
        return components(p)
        
    except Exception as e:
        logger.error(f"Error creating line chart: {e}")
        return None, None

@app.route('/')
def index():
    """Main page"""
    return render_template('index_new.html', 
                         title="Pacific Economy Dashboard",
                         categories=CATEGORIES,
                         data_info=f"Dataset contains {len(df)} records" if not df.empty else "No data available")

@app.route('/visualize', methods=['POST'])
def visualize():
    """Generate visualizations"""
    try:
        category = request.form.get('category')
        indicator = request.form.get('indicator')
        
        if not category or not indicator:
            flash('Please select both category and indicator', 'error')
            return render_template('index_new.html', 
                                 title="Pacific Economy Dashboard",
                                 categories=CATEGORIES,
                                 data_info=f"Dataset contains {len(df)} records" if not df.empty else "No data available")
        
        # Get indicator title
        indicator_title = CATEGORIES.get(category, {}).get('indicators', {}).get(indicator, indicator)
        
        # Clean data
        clean_df = clean_data(df, indicator)
        
        if clean_df.empty:
            flash(f'No data found for {indicator_title}', 'warning')
            return render_template('index_new.html', 
                                 title="Pacific Economy Dashboard",
                                 categories=CATEGORIES,
                                 selected_category=category,
                                 selected_indicator=indicator,
                                 data_info="No data available for selected indicator")
        
        # Create visualizations
        bar_script, bar_div = create_bar_chart(clean_df, indicator_title)
        box_script, box_div = create_box_plot(clean_df, indicator_title)
        line_script, line_div = create_line_chart(clean_df, indicator_title)
        
        flash(f'Visualizations created for {indicator_title}', 'success')
        
        return render_template('index_new.html',
                             title="Pacific Economy Dashboard",
                             categories=CATEGORIES,
                             selected_category=category,
                             selected_indicator=indicator,
                             indicator_title=indicator_title,
                             data_info=f"Showing {len(clean_df)} data points",
                             bar_script=bar_script, bar_div=bar_div,
                             box_script=box_script, box_div=box_div,
                             line_script=line_script, line_div=line_div)
    
    except Exception as e:
        logger.error(f"Error in visualize route: {e}")
        flash('Error creating visualizations', 'error')
        return render_template('index_new.html', 
                             title="Pacific Economy Dashboard",
                             categories=CATEGORIES,
                             data_info="Error occurred")

@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'data_loaded': not df.empty,
        'data_rows': len(df)
    }

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting app on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Data status: {'Loaded' if not df.empty else 'Failed'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
