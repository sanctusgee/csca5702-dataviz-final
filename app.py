import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="WA State EV Analytics Platform",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# I am adding this because I notice that the app is not responsive on mobile devices
# and I want to provide a toggle for mobile mode
if 'mobile_mode' not in st.session_state:
    st.session_state.mobile_mode = False

# Add mobile toggle in sidebar (after your existing filters)
st.sidebar.markdown("---")
if st.sidebar.button("Toggle Mobile Mode"):
    st.session_state.mobile_mode = not st.session_state.mobile_mode
    st.rerun()

if st.session_state.mobile_mode:
    st.sidebar.success("Mobile mode active")
    # Use smaller sample size for mobile, instead of 5000
    SAMPLE_SIZE = 1000
else:
    SAMPLE_SIZE = 5000  # current sample size for desktop


# I am using minimal CSS for my professional looking styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #2E86AB, #A23B72, #F18F01);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2E86AB;
        margin-bottom: 1rem;
        border-bottom: 3px solid #A23B72;
        padding-bottom: 0.5rem;
    }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: transform 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
    }

    .nav-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
        cursor: pointer;
    }

    .nav-card:hover {
        transform: translateY(-5px);
    }

    .insight-box {
        background: linear-gradient(135deg, #FF6B6B, #4ECDC4);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        font-weight: 600;
    }

    .clickable-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: transform 0.2s ease;
        border: none;
        width: 100%;
        text-align: left;
    }

    .clickable-section:hover {
        transform: translateX(5px);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }

    .price-tag {
        background: linear-gradient(135deg, #2ECC71, #27AE60);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.2rem;
    }

    .sidebar .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 10px;
    }

    .stAlert {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .footer-text {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid #eee;
    }

    .modern-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.3rem 0.8rem;
        border-radius: 8px;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .modern-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    .filter-counter {
        background: #4CAF50;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }

    .stMultiSelect > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e1e5e9;
    }

    .stMultiSelect > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.25);
    }
</style>
""", unsafe_allow_html=True)


# Data Loading and Caching
@st.cache_data(ttl=3600)
def load_data():
    """Load and preprocess the WA State EV dataset"""
    try:
        df = pd.read_csv("data/electric_vehicle_population.csv")

        # Clean and preprocess data
        df = df.dropna(subset=['Model Year', 'Make', 'Electric Vehicle Type', 'Electric Range'])
        df['Model Year'] = df['Model Year'].astype(int)
        df['Electric Range'] = pd.to_numeric(df['Electric Range'], errors='coerce')
        df = df[df['Electric Range'] > 0]

        # Clean MSRP data
        if 'Base MSRP' in df.columns:
            df['Base MSRP'] = pd.to_numeric(df['Base MSRP'], errors='coerce')
            df = df[df['Base MSRP'] > 0]  # Remove invalid prices

        # Create price categories
        if 'Base MSRP' in df.columns:
            df['Price_Category'] = pd.cut(
                df['Base MSRP'],
                bins=[0, 30000, 50000, 80000, float('inf')],
                labels=['Budget (<$30K)', 'Mid-Range ($30K-$50K)', 'Premium ($50K-$80K)', 'Luxury ($80K+)']
            )

        # Create range categories
        df['Range_Category'] = pd.cut(
            df['Electric Range'],
            bins=[0, 100, 200, 300, float('inf')],
            labels=['Short (<100mi)', 'Medium (100-200mi)', 'Long (200-300mi)', 'Ultra (300mi+)']
        )

        # Geographic processing
        if 'County' in df.columns:
            df['County'] = df['County'].str.title()
        if 'City' in df.columns:
            df['City'] = df['City'].str.title()

        # ALright - this is where I check for device type (mobile or desktop)
        if st.session_state.get('mobile_mode', False) and len(df) > 1000:
            df = df.sample(n=1000, random_state=42)
        elif len(df) > 5000:
            df = df.sample(n=5000, random_state=42)

        return df
    except FileNotFoundError:
        st.error("Dataset not found. Please ensure the WA State EV data is available.")
        return pd.DataFrame()


# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'df' not in st.session_state:
        st.session_state.df = load_data()

    if st.session_state.df.empty:
        return

    if 'selected_makes' not in st.session_state:
        st.session_state.selected_makes = st.session_state.df['Make'].unique().tolist()
    if 'selected_types' not in st.session_state:
        st.session_state.selected_types = st.session_state.df['Electric Vehicle Type'].unique().tolist()
    if 'selected_counties' not in st.session_state:
        if 'County' in st.session_state.df.columns:
            st.session_state.selected_counties = st.session_state.df['County'].unique().tolist()
        else:
            st.session_state.selected_counties = []
    if 'year_range' not in st.session_state:
        min_year = int(st.session_state.df['Model Year'].min())
        max_year = int(st.session_state.df['Model Year'].max())
        st.session_state.year_range = (min_year, max_year)
    if 'price_range' not in st.session_state and 'Base MSRP' in st.session_state.df.columns:
        min_price = int(st.session_state.df['Base MSRP'].min())
        max_price = int(st.session_state.df['Base MSRP'].max())
        st.session_state.price_range = (min_price, max_price)
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"


# Advanced Sidebar Filtering
def create_sidebar_filters():
    """Create comprehensive sidebar filters"""
    if st.session_state.df.empty:
        return None, None

    # Navigation at top of sidebar
    st.sidebar.markdown("### Navigate to Section")
    pages = {
        "Home": "home",
        "Executive Dashboard": "overview",
        "Price Analytics": "price",
        "Geographic Insights": "geographic",
        "Performance Analysis": "performance",
        "Market Leaders": "leaders",
        "Distribution Analysis": "distribution",
        "Market Share": "pie",
        "Box Analysis": "boxplot",
        "Heatmap Analysis": "heatmap",
        "Trends Analysis": "trends"
    }

    selected = st.sidebar.selectbox("Choose Page:", list(pages.keys()),
                                    index=list(pages.keys()).index(st.session_state.current_page),
                                    key="navigation_selectbox")

    # Only update if selection actually changed
    if selected != st.session_state.current_page:
        st.session_state.current_page = selected
        st.rerun()

    # Real-Time Analytics at top
    st.sidebar.markdown("### Real-Time Analytics")
    if not st.session_state.df.empty:
        # Quick preview metrics before filtering
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Total Vehicles", f"{len(st.session_state.df):,}")
            if 'Base MSRP' in st.session_state.df.columns:
                avg_price = st.session_state.df['Base MSRP'].mean()
                st.metric("Avg Price", f"${avg_price:,.0f}")
        with col2:
            avg_range = st.session_state.df['Electric Range'].mean()
            st.metric("Avg Range", f"{avg_range:.0f} mi")
            if 'County' in st.session_state.df.columns:
                unique_counties = st.session_state.df['County'].nunique()
                st.metric("Counties", f"{unique_counties}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Advanced Filter Controls")

    # Year Range Slider
    min_year = int(st.session_state.df['Model Year'].min())
    max_year = int(st.session_state.df['Model Year'].max())
    year_range = st.sidebar.slider(
        "Model Year Range",
        min_value=min_year,
        max_value=max_year,
        value=st.session_state.year_range,
        key="year_slider"
    )
    st.session_state.year_range = year_range

    # Price Range Filter (if available)
    price_filter = None
    if 'Base MSRP' in st.session_state.df.columns:
        st.sidebar.markdown("#### Price Range")
        min_price = int(st.session_state.df['Base MSRP'].min())
        max_price = int(st.session_state.df['Base MSRP'].max())
        price_filter = st.sidebar.slider(
            "MSRP ($)",
            min_value=min_price,
            max_value=max_price,
            value=st.session_state.price_range,
            format="$%d",
            key="price_slider"
        )
        st.session_state.price_range = price_filter

    # Initialize variables
    selected_counties = []

    # Geographic Filters - Modern Interface
    if 'County' in st.session_state.df.columns:
        st.sidebar.markdown("#### Geographic Filters")
        counties = sorted(st.session_state.df['County'].dropna().unique().tolist())

        # Ensure selected_counties are valid
        if not st.session_state.selected_counties:
            st.session_state.selected_counties = counties
        valid_selected_counties = [c for c in st.session_state.selected_counties if c in counties]
        if not valid_selected_counties:
            valid_selected_counties = counties
        st.session_state.selected_counties = valid_selected_counties

        # Modern filter interface
        st.sidebar.markdown("**Counties** (Select one or more)")
        col1, col2 = st.sidebar.columns([1, 1])
        with col1:
            if st.button("All", key="select_all_counties", help="Select all counties"):
                st.session_state.selected_counties = counties
                st.rerun()
        with col2:
            if st.button("Clear", key="clear_counties", help="Clear all selections"):
                st.session_state.selected_counties = []
                st.rerun()

        # Modern multiselect with better UX
        selected_counties = st.sidebar.multiselect(
            "",
            counties,
            default=st.session_state.selected_counties,
            key="counties_multiselect",
            help=f"Select from {len(counties)} available counties"
        )

        # Update session state only if changed
        if selected_counties != st.session_state.selected_counties:
            st.session_state.selected_counties = selected_counties

    # Makes Selection - Modern Interface
    st.sidebar.markdown("#### Vehicle Makes")
    makes = sorted(st.session_state.df['Make'].unique().tolist())

    # Ensure selected_makes are valid
    if not st.session_state.selected_makes:
        st.session_state.selected_makes = makes
    valid_selected_makes = [m for m in st.session_state.selected_makes if m in makes]
    if not valid_selected_makes:
        valid_selected_makes = makes
    st.session_state.selected_makes = valid_selected_makes

    # Modern filter interface
    st.sidebar.markdown(f"**Makes** ({len(st.session_state.selected_makes)}/{len(makes)} selected)")
    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        if st.button("All", key="select_all_makes", help="Select all makes"):
            st.session_state.selected_makes = makes
            st.rerun()
    with col2:
        if st.button("Clear", key="clear_makes", help="Clear all selections"):
            st.session_state.selected_makes = []
            st.rerun()

    selected_makes = st.sidebar.multiselect(
        "",
        makes,
        default=st.session_state.selected_makes,
        key="makes_multiselect",
        help=f"Select from {len(makes)} available makes"
    )

    # Update session state only if changed
    if selected_makes != st.session_state.selected_makes:
        st.session_state.selected_makes = selected_makes

    # Vehicle Types Selection - Modern Interface
    st.sidebar.markdown("#### Vehicle Types")
    vehicle_types = sorted(st.session_state.df['Electric Vehicle Type'].unique().tolist())

    # Ensure selected_types are valid
    if not st.session_state.selected_types:
        st.session_state.selected_types = vehicle_types
    valid_selected_types = [t for t in st.session_state.selected_types if t in vehicle_types]
    if not valid_selected_types:
        valid_selected_types = vehicle_types
    st.session_state.selected_types = valid_selected_types

    # Modern filter interface
    st.sidebar.markdown(f"**Types** ({len(st.session_state.selected_types)}/{len(vehicle_types)} selected)")
    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        if st.button("All", key="select_all_types", help="Select all types"):
            st.session_state.selected_types = vehicle_types
            st.rerun()
    with col2:
        if st.button("Clear", key="clear_types", help="Clear all selections"):
            st.session_state.selected_types = []
            st.rerun()

    selected_types = st.sidebar.multiselect(
        "",
        vehicle_types,
        default=st.session_state.selected_types,
        key="types_multiselect",
        help=f"Select from {len(vehicle_types)} available types"
    )

    # Update session state only if changed
    if selected_types != st.session_state.selected_types:
        st.session_state.selected_types = selected_types

    # CAFV Eligibility Filter
    if 'Clean Alternative Fuel Vehicle (CAFV) Eligibility' in st.session_state.df.columns:
        st.sidebar.markdown("#### CAFV Eligibility")
        cafv_eligible = st.sidebar.checkbox("CAFV Eligible Only", value=False, key="cafv_filter")
    else:
        cafv_eligible = False

    # Electric Range Filter
    st.sidebar.markdown("#### Electric Range Filter")
    min_range = int(st.session_state.df['Electric Range'].min())
    max_range = int(st.session_state.df['Electric Range'].max())
    range_filter = st.sidebar.slider(
        "Range (miles)",
        min_value=min_range,
        max_value=max_range,
        value=(min_range, max_range),
        key="range_slider"
    )

    # Start with base dataframe and apply filters step by step
    filtered_df = st.session_state.df.copy()

    # Apply all filters (ensuring we don't filter if no selections)
    if selected_makes:  # Only filter if there are selected makes
        filtered_df = filtered_df[filtered_df['Make'].isin(selected_makes)]
    if selected_types:  # Only filter if there are selected types
        filtered_df = filtered_df[filtered_df['Electric Vehicle Type'].isin(selected_types)]

    filtered_df = filtered_df[
        (filtered_df['Model Year'] >= year_range[0]) &
        (filtered_df['Model Year'] <= year_range[1]) &
        (filtered_df['Electric Range'] >= range_filter[0]) &
        (filtered_df['Electric Range'] <= range_filter[1])
        ]

    # Apply geographic filter
    if 'County' in st.session_state.df.columns and selected_counties:
        filtered_df = filtered_df[filtered_df['County'].isin(selected_counties)]

    # Apply price filter
    if price_filter and 'Base MSRP' in st.session_state.df.columns:
        filtered_df = filtered_df[
            (filtered_df['Base MSRP'] >= price_filter[0]) &
            (filtered_df['Base MSRP'] <= price_filter[1])
            ]

    # Apply CAFV filter
    if cafv_eligible and 'Clean Alternative Fuel Vehicle (CAFV) Eligibility' in st.session_state.df.columns:
        filtered_df = filtered_df[filtered_df['Clean Alternative Fuel Vehicle (CAFV) Eligibility'].notna()]

    # Sample Mode
    st.sidebar.markdown("#### Display Options")
    use_sample = st.sidebar.checkbox("Sample Mode (5,000 points)", value=True, key="sample_mode")

    total_records = len(filtered_df)
    if use_sample and total_records > 5000:
        display_df = filtered_df.sample(n=5000, random_state=42)
        st.sidebar.warning(f"Showing 5,000 of {total_records:,} records")
    else:
        display_df = filtered_df
        st.sidebar.success(f"Showing all {total_records:,} records")

    # Updated Dataset Info after filtering
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filtered Results")
    if not filtered_df.empty:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Filtered Total", f"{total_records:,}")
            if 'Base MSRP' in filtered_df.columns:
                filtered_avg_price = filtered_df['Base MSRP'].mean()
                st.metric("Filtered Avg Price", f"${filtered_avg_price:,.0f}")
        with col2:
            filtered_avg_range = filtered_df['Electric Range'].mean()
            st.metric("Filtered Avg Range", f"{filtered_avg_range:.0f} mi")
            if 'County' in filtered_df.columns:
                filtered_unique_counties = filtered_df['County'].nunique()
                st.metric("Filtered Counties", f"{filtered_unique_counties}")

    return filtered_df, display_df


# Color Schemes and Selections
def get_color_schemes():
    """Define professional color schemes for Altair"""
    return {
        'categorical': 'category20',
        'sequential': 'viridis',
        'diverging': 'redyellowblue',
        'makes': 'set3',
        'types': 'dark2',
        'price': 'plasma',
        'geographic': 'blues',
        'performance': 'turbo'
    }


def create_selections():
    """Create Altair selections for interactivity"""
    click_selection = alt.selection_point(fields=['Electric Vehicle Type'])
    brush_selection = alt.selection_interval()
    return click_selection, brush_selection


# Individual Page Functions
def home_page():
    """Enhanced landing page with comprehensive overview"""
    st.markdown('<h1 class="main-header">Washington State EV Analytics Platform</h1>', unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: center; font-size: 1.3rem; color: #666; margin-bottom: 3rem;'>
        Submitted for final project CSCA 5702 - Fundamentals of Data Visualization<br>
        <strong>GitHub:</strong> <a href="https://sanctusgee/csca5702-dataviz-final.git" target="_blank">CSCA5702-Final-Project</a>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced key metrics overview
    if not st.session_state.df.empty:
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            total_vehicles = len(st.session_state.df)
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total EVs</h3>
                <h2>{total_vehicles:,}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            unique_makes = st.session_state.df['Make'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <h3>Brands</h3>
                <h2>{unique_makes}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            if 'Base MSRP' in st.session_state.df.columns:
                avg_price = st.session_state.df['Base MSRP'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Avg Price</h3>
                    <h2>${avg_price:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)

        with col4:
            avg_range = st.session_state.df['Electric Range'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h3>Avg Range</h3>
                <h2>{avg_range:.0f} mi</h2>
            </div>
            """, unsafe_allow_html=True)

        with col5:
            if 'County' in st.session_state.df.columns:
                counties = st.session_state.df['County'].nunique()
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Counties</h3>
                    <h2>{counties}</h2>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Market insights
    if not st.session_state.df.empty:
        st.markdown('<h2 class="sub-header">Key Market Insights</h2>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            # Top Make
            top_make = st.session_state.df['Make'].value_counts().index[0]
            top_make_count = st.session_state.df['Make'].value_counts().iloc[0]
            st.markdown(f"""
            <div class="insight-box">
                Market Leader: <strong>{top_make}</strong><br>
                {top_make_count:,} vehicles ({top_make_count / len(st.session_state.df) * 100:.1f}% market share)
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Price insights
            if 'Base MSRP' in st.session_state.df.columns:
                median_price = st.session_state.df['Base MSRP'].median()
                luxury_percent = (st.session_state.df['Base MSRP'] > 80000).mean() * 100
                st.markdown(f"""
                <div class="insight-box">
                    Median Price: <strong>${median_price:,.0f}</strong><br>
                    {luxury_percent:.1f}% are luxury vehicles ($80K+)
                </div>
                """, unsafe_allow_html=True)

        with col3:
            # Range insights
            long_range_percent = (st.session_state.df['Electric Range'] > 300).mean() * 100
            max_range = st.session_state.df['Electric Range'].max()
            st.markdown(f"""
            <div class="insight-box">
                Max Range: <strong>{max_range:.0f} miles</strong><br>
                {long_range_percent:.1f}% have 300+ mile range
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation guide with clickable sections
    st.markdown('<h2 class="sub-header">Explore Advanced Analytics</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
                "**Price Analytics**\n• MSRP vs Range performance analysis\n• Affordability trends by region\n• Value proposition insights",
                key="price_nav", help="Click to navigate to Price Analytics"):
            st.session_state.current_page = "Price Analytics"
            st.rerun()

        if st.button(
                "**Geographic Insights**\n• County-level adoption patterns\n• Urban vs rural preferences\n• Regional market characteristics",
                key="geo_nav", help="Click to navigate to Geographic Insights"):
            st.session_state.current_page = "Geographic Insights"
            st.rerun()

        if st.button(
                "**Performance Analysis**\n• Range distribution analysis\n• Technology advancement trends\n• Efficiency improvements",
                key="perf_nav", help="Click to navigate to Performance Analysis"):
            st.session_state.current_page = "Performance Analysis"
            st.rerun()

        if st.button(
                "**Market Leaders**\n• Brand performance rankings\n• Model popularity analysis\n• Competitive landscape",
                key="leaders_nav", help="Click to navigate to Market Leaders"):
            st.session_state.current_page = "Market Leaders"
            st.rerun()

    with col2:
        if st.button(
                "**Distribution Analysis**\n• Electric range histograms\n• Statistical distribution insights\n• Frequency analysis by vehicle type",
                key="dist_nav", help="Click to navigate to Distribution Analysis"):
            st.session_state.current_page = "Distribution Analysis"
            st.rerun()

        if st.button(
                "**Market Share**\n• Vehicle type market composition\n• Interactive pie chart visualization\n• Proportional analysis",
                key="share_nav", help="Click to navigate to Market Share"):
            st.session_state.current_page = "Market Share"
            st.rerun()

        if st.button(
                "**Box Analysis**\n• Range distribution by vehicle type\n• Outlier identification\n• Statistical quartile analysis",
                key="box_nav", help="Click to navigate to Box Analysis"):
            st.session_state.current_page = "Box Analysis"
            st.rerun()

        if st.button(
                "**Heatmap Analysis**\n• Make vs. model year correlation\n• Time-based trend analysis\n• Pattern recognition",
                key="heatmap_nav", help="Click to navigate to Heatmap Analysis"):
            st.session_state.current_page = "Heatmap Analysis"
            st.rerun()

    # Footer
    st.markdown("""
    <div class="footer-text">
        Data source: (c) Washington State Department of Licensing - https://data.wa.gov/Transportation/Electric-Vehicle-Population-Data/f6w7-q2d2/about_data<br>
        Electric Vehicle Population Data
    </div>
    """, unsafe_allow_html=True)


def overview_page(filtered_df, display_df):
    """Executive dashboard with comprehensive KPIs"""
    st.markdown('<h1 class="main-header">Executive Dashboard</h1>', unsafe_allow_html=True)

    # Return to Home button
    if st.button("Return to Home", key="overview_home", help="Go back to home page"):
        st.session_state.current_page = "Home"
        st.rerun()

    if filtered_df.empty:
        st.warning("No data available with current filters. Please adjust your selection.")
        return

    # Executive KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_vehicles = len(filtered_df)
        growth_rate = calculate_growth_rate(filtered_df)
        st.metric(
            "Total Vehicles",
            f"{total_vehicles:,}",
            f"{growth_rate:+.1f}% YoY" if growth_rate else None
        )

    with col2:
        if 'Base MSRP' in filtered_df.columns:
            avg_price = filtered_df['Base MSRP'].mean()
            price_trend = calculate_price_trend(filtered_df)
            st.metric(
                "Average Price",
                f"${avg_price:,.0f}",
                f"{price_trend:+.1f}%" if price_trend else None
            )

    with col3:
        avg_range = filtered_df['Electric Range'].mean()
        range_trend = calculate_range_trend(filtered_df)
        st.metric(
            "Average Range",
            f"{avg_range:.0f} mi",
            f"{range_trend:+.1f}%" if range_trend else None
        )

    with col4:
        market_concentration = calculate_market_concentration(filtered_df)
        st.metric("Market Concentration", f"{market_concentration:.1f}%")

    # Main dashboard charts
    col1, col2 = st.columns(2)

    with col1:
        # Market share evolution
        if len(filtered_df) > 100:
            yearly_trends = filtered_df.groupby(['Model Year', 'Electric Vehicle Type']).size().reset_index(
                name='Count')

            chart = alt.Chart(yearly_trends).mark_area().encode(
                x=alt.X('Model Year:O', title='Model Year'),
                y=alt.Y('Count:Q', title='Number of Vehicles'),
                color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='category20')),
                tooltip=['Model Year', 'Electric Vehicle Type', 'Count']
            ).properties(
                width=350,
                height=400,
                title="Market Evolution by Vehicle Type"
            )
            st.altair_chart(chart, use_container_width=True)

    with col2:
        # Price vs Performance scatter
        if 'Base MSRP' in filtered_df.columns:
            scatter = alt.Chart(display_df).mark_circle(size=60, opacity=0.7).encode(
                x=alt.X('Electric Range:Q', title='Electric Range (miles)'),
                y=alt.Y('Base MSRP:Q', title='Base MSRP ($)', scale=alt.Scale(type='log')),
                color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='dark2')),
                size=alt.Size('Model Year:O', scale=alt.Scale(range=[50, 200])),
                tooltip=['Make', 'Model', 'Electric Range', 'Base MSRP', 'Electric Vehicle Type']
            ).properties(
                width=350,
                height=400,
                title="Price vs Performance Matrix"
            ).interactive()
            st.altair_chart(scatter, use_container_width=True)

    # Geographic and competitive analysis
    col1, col2 = st.columns(2)

    with col1:
        # Top performing counties
        if 'County' in filtered_df.columns:
            county_adoption = filtered_df['County'].value_counts().head(10).reset_index()
            county_adoption.columns = ['County', 'Count']

            bar_chart = alt.Chart(county_adoption).mark_bar().encode(
                x=alt.X('Count:Q', title='Number of Vehicles'),
                y=alt.Y('County:N', sort='-x', title='County'),
                color=alt.Color('Count:Q', scale=alt.Scale(scheme='viridis')),
                tooltip=['County', 'Count']
            ).properties(
                width=350,
                height=400,
                title="Top Counties by EV Adoption"
            )
            st.altair_chart(bar_chart, use_container_width=True)

    with col2:
        # Brand market share
        brand_share = filtered_df['Make'].value_counts().head(8).reset_index()
        brand_share.columns = ['Make', 'Count']

        pie_chart = alt.Chart(brand_share).mark_arc().encode(
            theta=alt.Theta('Count:Q'),
            color=alt.Color('Make:N', scale=alt.Scale(scheme='set3')),
            tooltip=['Make', 'Count']
        ).properties(
            width=350,
            height=400,
            title="Brand Market Share (Top 8)"
        )
        st.altair_chart(pie_chart, use_container_width=True)


def price_page(filtered_df, display_df):
    """Advanced price analytics page"""
    st.markdown('<h1 class="main-header">Price Analytics Dashboard</h1>', unsafe_allow_html=True)

    # Return to Home button
    if st.button("Return to Home", key="price_home", help="Go back to home page"):
        st.session_state.current_page = "Home"
        st.rerun()

    if 'Base MSRP' not in filtered_df.columns:
        st.error("Price data not available in the dataset.")
        return

    if filtered_df.empty:
        st.warning("No data available with current filters.")
        return

    # Price distribution overview
    col1, col2, col3 = st.columns(3)

    with col1:
        median_price = filtered_df['Base MSRP'].median()
        st.metric("Median Price", f"${median_price:,.0f}")

    with col2:
        luxury_count = (filtered_df['Base MSRP'] > 80000).sum()
        luxury_percent = (luxury_count / len(filtered_df)) * 100
        st.metric("Luxury Vehicles", f"{luxury_count:,} ({luxury_percent:.1f}%)")

    with col3:
        affordable_count = (filtered_df['Base MSRP'] < 30000).sum()
        affordable_percent = (affordable_count / len(filtered_df)) * 100
        st.metric("Affordable (<$30K)", f"{affordable_count:,} ({affordable_percent:.1f}%)")

    # Price analysis charts
    col1, col2 = st.columns(2)

    with col1:
        # Price distribution histogram
        histogram = alt.Chart(filtered_df).mark_bar().encode(
            x=alt.X('Base MSRP:Q', bin=alt.Bin(maxbins=30), title='Base MSRP ($)'),
            y=alt.Y('count()', title='Number of Vehicles'),
            color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='dark2')),
            tooltip=['count()']
        ).properties(
            width=350,
            height=400,
            title="Price Distribution by Vehicle Type"
        )
        st.altair_chart(histogram, use_container_width=True)

    with col2:
        # Price efficiency analysis
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['Price_per_Mile'] = filtered_df_copy['Base MSRP'] / filtered_df_copy['Electric Range']
        efficiency_data = filtered_df_copy.groupby('Make')['Price_per_Mile'].mean().sort_values().head(10).reset_index()

        efficiency_chart = alt.Chart(efficiency_data).mark_bar().encode(
            x=alt.X('Price_per_Mile:Q', title='Price per Mile ($)'),
            y=alt.Y('Make:N', sort='-x', title='Make'),
            color=alt.Color('Price_per_Mile:Q', scale=alt.Scale(scheme='plasma')),
            tooltip=['Make', alt.Tooltip('Price_per_Mile:Q', format='.2f')]
        ).properties(
            width=350,
            height=400,
            title="Price Efficiency by Make"
        )
        st.altair_chart(efficiency_chart, use_container_width=True)

    # Advanced price analysis
    col1, col2 = st.columns(2)

    with col1:
        # Price trends over time
        price_trends = filtered_df.groupby(['Model Year', 'Electric Vehicle Type'])['Base MSRP'].mean().reset_index()

        trend_chart = alt.Chart(price_trends).mark_line(point=True).encode(
            x=alt.X('Model Year:O', title='Model Year'),
            y=alt.Y('Base MSRP:Q', title='Average Price ($)'),
            color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='category20')),
            tooltip=['Model Year', 'Electric Vehicle Type', alt.Tooltip('Base MSRP:Q', format='$,.0f')]
        ).properties(
            width=350,
            height=400,
            title="Average Price Trends Over Time"
        )
        st.altair_chart(trend_chart, use_container_width=True)

    with col2:
        # Price categories
        if 'Price_Category' in filtered_df.columns:
            price_cat_dist = filtered_df['Price_Category'].value_counts().reset_index()
            price_cat_dist.columns = ['Category', 'Count']

            pie_chart = alt.Chart(price_cat_dist).mark_arc().encode(
                theta=alt.Theta('Count:Q'),
                color=alt.Color('Category:N', scale=alt.Scale(scheme='plasma')),
                tooltip=['Category', 'Count']
            ).properties(
                width=350,
                height=400,
                title="Market Segmentation by Price"
            )
            st.altair_chart(pie_chart, use_container_width=True)


def geographic_page(filtered_df, display_df):
    """Geographic insights and analysis"""
    st.markdown('<h1 class="main-header">Geographic Market Insights</h1>', unsafe_allow_html=True)

    # Return to Home button
    if st.button("Return to Home", key="geo_home", help="Go back to home page"):
        st.session_state.current_page = "Home"
        st.rerun()

    if 'County' not in filtered_df.columns:
        st.error("Geographic data not available in the dataset.")
        return

    if filtered_df.empty:
        st.warning("No data available with current filters.")
        return

    # Geographic overview metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_counties = filtered_df['County'].nunique()
        st.metric("Counties Covered", total_counties)

    with col2:
        if 'City' in filtered_df.columns:
            total_cities = filtered_df['City'].nunique()
            st.metric("Cities", total_cities)

    with col3:
        top_county = filtered_df['County'].value_counts().index[0]
        top_county_count = filtered_df['County'].value_counts().iloc[0]
        st.metric("Leading County", f"{top_county} ({top_county_count:,})")

    with col4:
        county_adoption_rate = len(filtered_df) / total_counties
        st.metric("Avg per County", f"{county_adoption_rate:.0f}")

    # Main geographic visualizations
    col1, col2 = st.columns(2)

    with col1:
        # County adoption ranking
        county_counts = filtered_df['County'].value_counts().head(15).reset_index()
        county_counts.columns = ['County', 'Count']

        bar_chart = alt.Chart(county_counts).mark_bar().encode(
            x=alt.X('Count:Q', title='Number of Vehicles'),
            y=alt.Y('County:N', sort='-x', title='County'),
            color=alt.Color('Count:Q', scale=alt.Scale(scheme='blues')),
            tooltip=['County', 'Count']
        ).properties(
            width=350,
            height=500,
            title="Top 15 Counties by EV Adoption"
        )
        st.altair_chart(bar_chart, use_container_width=True)

    with col2:
        # Vehicle type distribution by counties
        top_counties = filtered_df['County'].value_counts().head(8).index
        county_type_data = filtered_df[filtered_df['County'].isin(top_counties)]
        county_type_dist = county_type_data.groupby(['County', 'Electric Vehicle Type']).size().reset_index(
            name='Count')

        stacked_bar = alt.Chart(county_type_dist).mark_bar().encode(
            x=alt.X('County:N', title='County'),
            y=alt.Y('Count:Q', title='Number of Vehicles'),
            color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='dark2')),
            tooltip=['County', 'Electric Vehicle Type', 'Count']
        ).properties(
            width=350,
            height=500,
            title="Vehicle Types by Top Counties"
        )
        st.altair_chart(stacked_bar, use_container_width=True)


def performance_page(filtered_df, display_df):
    """Performance and range analysis"""
    st.markdown('<h1 class="main-header">Performance Analytics</h1>', unsafe_allow_html=True)

    # Return to Home button
    if st.button("Return to Home", key="perf_home", help="Go back to home page"):
        st.session_state.current_page = "Home"
        st.rerun()

    if filtered_df.empty:
        st.warning("No data available with current filters.")
        return

    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        max_range = filtered_df['Electric Range'].max()
        max_range_vehicle = filtered_df[filtered_df['Electric Range'] == max_range][['Make', 'Model']].iloc[0]
        st.metric("Max Range", f"{max_range:.0f} mi", f"{max_range_vehicle['Make']} {max_range_vehicle['Model']}")

    with col2:
        long_range_count = (filtered_df['Electric Range'] > 300).sum()
        long_range_percent = (long_range_count / len(filtered_df)) * 100
        st.metric("Long Range (300mi+)", f"{long_range_count:,} ({long_range_percent:.1f}%)")

    with col3:
        range_improvement = calculate_range_improvement(filtered_df)
        st.metric("Range Improvement", f"{range_improvement:.1f}%" if range_improvement else "N/A")

    with col4:
        avg_range_by_year = filtered_df.groupby('Model Year')['Electric Range'].mean()
        if len(avg_range_by_year) > 1:
            latest_avg = avg_range_by_year.iloc[-1]
            st.metric("Latest Avg Range", f"{latest_avg:.0f} mi")

    # Range analysis charts
    col1, col2 = st.columns(2)

    with col1:
        # Range evolution over time
        range_trends = filtered_df.groupby(['Model Year', 'Electric Vehicle Type'])[
            'Electric Range'].mean().reset_index()

        trend_chart = alt.Chart(range_trends).mark_line(point=True).encode(
            x=alt.X('Model Year:O', title='Model Year'),
            y=alt.Y('Electric Range:Q', title='Average Range (miles)'),
            color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='category20')),
            tooltip=['Model Year', 'Electric Vehicle Type', alt.Tooltip('Electric Range:Q', format='.1f')]
        ).properties(
            width=350,
            height=400,
            title="Range Evolution by Vehicle Type"
        )
        st.altair_chart(trend_chart, use_container_width=True)

    with col2:
        # Top performers by make
        make_performance = filtered_df.groupby('Make').agg({
            'Electric Range': ['mean', 'max', 'count']
        }).round(1)
        make_performance.columns = ['Avg_Range', 'Max_Range', 'Count']
        make_performance = make_performance[make_performance['Count'] >= 5].sort_values('Avg_Range',
                                                                                        ascending=False).head(
            10).reset_index()

        scatter_performance = alt.Chart(make_performance).mark_circle(size=100).encode(
            x=alt.X('Avg_Range:Q', title='Average Range (miles)'),
            y=alt.Y('Max_Range:Q', title='Maximum Range (miles)'),
            size=alt.Size('Count:Q', scale=alt.Scale(range=[100, 400])),
            color=alt.Color('Make:N', scale=alt.Scale(scheme='set3')),
            tooltip=['Make', 'Avg_Range', 'Max_Range', 'Count']
        ).properties(
            width=350,
            height=400,
            title="Make Performance Matrix"
        )
        st.altair_chart(scatter_performance, use_container_width=True)


def distribution_page(filtered_df, display_df):
    """Distribution analysis page"""
    st.markdown('<h1 class="main-header">Distribution Analysis</h1>', unsafe_allow_html=True)

    # Return to Home button
    if st.button("Return to Home", key="dist_home", help="Go back to home page"):
        st.session_state.current_page = "Home"
        st.rerun()

    if display_df.empty:
        st.warning("No data available with current filters.")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Histogram with overlaid curves
        histogram = alt.Chart(display_df).mark_bar(opacity=0.7).encode(
            x=alt.X('Electric Range:Q', bin=alt.Bin(maxbins=30), title='Electric Range (miles)'),
            y=alt.Y('count()', title='Number of Vehicles'),
            color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='dark2')),
            tooltip=['count()']
        ).properties(
            width=350,
            height=500,
            title="Electric Range Distribution by Type"
        )
        st.altair_chart(histogram, use_container_width=True)

    with col2:
        # Box plot analysis
        box_plot = alt.Chart(display_df).mark_boxplot(size=50).encode(
            x=alt.X('Electric Vehicle Type:N', title='Vehicle Type'),
            y=alt.Y('Electric Range:Q', title='Electric Range (miles)'),
            color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='dark2'))
        ).properties(
            width=350,
            height=500,
            title="Range Distribution by Vehicle Type"
        )
        st.altair_chart(box_plot, use_container_width=True)

    # Additional distribution metrics
    st.markdown("### Statistical Summary")

    stats_df = display_df.groupby('Electric Vehicle Type')['Electric Range'].agg([
        'count', 'mean', 'median', 'std', 'min', 'max'
    ]).round(2)

    st.dataframe(stats_df, use_container_width=True)


def pie_page(filtered_df, display_df):
    """Pie chart and market share analysis"""
    st.markdown('<h1 class="main-header">Market Share Analysis</h1>', unsafe_allow_html=True)

    # Return to Home button
    if st.button("Return to Home", key="pie_home", help="Go back to home page"):
        st.session_state.current_page = "Home"
        st.rerun()

    if filtered_df.empty:
        st.warning("No data available with current filters.")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Vehicle Type Market Share
        type_counts = filtered_df['Electric Vehicle Type'].value_counts().reset_index()
        type_counts.columns = ['Type', 'Count']

        pie_type = alt.Chart(type_counts).mark_arc().encode(
            theta=alt.Theta('Count:Q'),
            color=alt.Color('Type:N', scale=alt.Scale(scheme='dark2')),
            tooltip=['Type', 'Count']
        ).properties(
            width=350,
            height=400,
            title="Market Share by Vehicle Type"
        )
        st.altair_chart(pie_type, use_container_width=True)

    with col2:
        # Top Makes Market Share
        make_counts = filtered_df['Make'].value_counts().head(8).reset_index()
        make_counts.columns = ['Make', 'Count']

        pie_make = alt.Chart(make_counts).mark_arc().encode(
            theta=alt.Theta('Count:Q'),
            color=alt.Color('Make:N', scale=alt.Scale(scheme='set3')),
            tooltip=['Make', 'Count']
        ).properties(
            width=350,
            height=400,
            title="Top 8 Makes Market Share"
        )
        st.altair_chart(pie_make, use_container_width=True)


def boxplot_page(filtered_df, display_df):
    """Box plot analysis page"""
    st.markdown('<h1 class="main-header">Box Plot Analysis</h1>', unsafe_allow_html=True)

    # Return to Home button
    if st.button("Return to Home", key="box_home", help="Go back to home page"):
        st.session_state.current_page = "Home"
        st.rerun()

    if display_df.empty:
        st.warning("No data available with current filters.")
        return

    # Main box plot
    box_plot = alt.Chart(display_df).mark_boxplot().encode(
        x=alt.X('Electric Vehicle Type:N', title='Vehicle Type'),
        y=alt.Y('Electric Range:Q', title='Electric Range (miles)'),
        color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='dark2'))
    ).properties(
        width=700,
        height=500,
        title="Electric Range Distribution by Vehicle Type"
    )
    st.altair_chart(box_plot, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Box plot by top makes
        top_makes = filtered_df['Make'].value_counts().head(8).index
        top_makes_df = display_df[display_df['Make'].isin(top_makes)]

        box_makes = alt.Chart(top_makes_df).mark_boxplot().encode(
            x=alt.X('Make:N', title='Make'),
            y=alt.Y('Electric Range:Q', title='Electric Range (miles)'),
            color=alt.Color('Make:N', scale=alt.Scale(scheme='set3'))
        ).properties(
            width=350,
            height=400,
            title="Range by Top Makes"
        )
        st.altair_chart(box_makes, use_container_width=True)

    with col2:
        # Violin plot alternative
        violin_plot = alt.Chart(display_df).mark_area(
            orient='horizontal',
            opacity=0.7
        ).transform_density(
            'Electric Range',
            as_=['Electric Range', 'density'],
            groupby=['Electric Vehicle Type']
        ).encode(
            x=alt.X('density:Q', title='Density'),
            y=alt.Y('Electric Range:Q', title='Electric Range (miles)'),
            color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='dark2'))
        ).properties(
            width=350,
            height=400,
            title="Range Density by Type"
        )
        st.altair_chart(violin_plot, use_container_width=True)


def heatmap_page(filtered_df, display_df):
    """Heatmap analysis page"""
    st.markdown('<h1 class="main-header">Heatmap Analysis</h1>', unsafe_allow_html=True)

    # Return to Home button
    if st.button("Return to Home", key="heatmap_home", help="Go back to home page"):
        st.session_state.current_page = "Home"
        st.rerun()

    if filtered_df.empty:
        st.warning("No data available with current filters.")
        return

    # Create heatmap data
    heatmap_data = filtered_df.groupby(['Make', 'Model Year']).size().reset_index(name='Count')

    # Limit to top makes for readability
    top_makes = filtered_df['Make'].value_counts().head(15).index
    heatmap_data = heatmap_data[heatmap_data['Make'].isin(top_makes)]

    heatmap = alt.Chart(heatmap_data).mark_rect().encode(
        x=alt.X('Model Year:O', title='Model Year'),
        y=alt.Y('Make:N', title='Make'),
        color=alt.Color('Count:Q', scale=alt.Scale(scheme='viridis'), title='Vehicle Count'),
        tooltip=['Make', 'Model Year', 'Count']
    ).properties(
        width=700,
        height=600,
        title="Vehicle Count Heatmap: Make vs Model Year"
    )
    st.altair_chart(heatmap, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Average range heatmap
        avg_range_data = filtered_df.groupby(['Electric Vehicle Type', 'Model Year'])[
            'Electric Range'].mean().reset_index()

        range_heatmap = alt.Chart(avg_range_data).mark_rect().encode(
            x=alt.X('Model Year:O', title='Model Year'),
            y=alt.Y('Electric Vehicle Type:N', title='Vehicle Type'),
            color=alt.Color('Electric Range:Q', scale=alt.Scale(scheme='plasma'), title='Avg Range'),
            tooltip=['Electric Vehicle Type', 'Model Year', alt.Tooltip('Electric Range:Q', format='.1f')]
        ).properties(
            width=350,
            height=400,
            title="Average Range Heatmap"
        )
        st.altair_chart(range_heatmap, use_container_width=True)

    with col2:
        # Price heatmap (if available)
        if 'Base MSRP' in filtered_df.columns:
            price_data = filtered_df.groupby(['Electric Vehicle Type', 'Model Year'])['Base MSRP'].mean().reset_index()

            price_heatmap = alt.Chart(price_data).mark_rect().encode(
                x=alt.X('Model Year:O', title='Model Year'),
                y=alt.Y('Electric Vehicle Type:N', title='Vehicle Type'),
                color=alt.Color('Base MSRP:Q', scale=alt.Scale(scheme='blues'), title='Avg Price'),
                tooltip=['Electric Vehicle Type', 'Model Year', alt.Tooltip('Base MSRP:Q', format='$,.0f')]
            ).properties(
                width=350,
                height=400,
                title="Average Price Heatmap"
            )
            st.altair_chart(price_heatmap, use_container_width=True)


def trends_page(filtered_df, display_df):
    """Trends analysis page"""
    st.markdown('<h1 class="main-header">Trend Analysis</h1>', unsafe_allow_html=True)

    # Return to Home button
    if st.button("Return to Home", key="trends_home", help="Go back to home page"):
        st.session_state.current_page = "Home"
        st.rerun()

    if filtered_df.empty:
        st.warning("No data available with current filters.")
        return

    # Average range trends over time
    range_trends = filtered_df.groupby(['Model Year', 'Electric Vehicle Type'])['Electric Range'].mean().reset_index()

    trend_chart = alt.Chart(range_trends).mark_line(point=True).encode(
        x=alt.X('Model Year:O', title='Model Year'),
        y=alt.Y('Electric Range:Q', title='Average Electric Range (miles)'),
        color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='dark2')),
        tooltip=['Model Year', 'Electric Vehicle Type', alt.Tooltip('Electric Range:Q', format='.1f')]
    ).properties(
        width=700,
        height=500,
        title="Average Electric Range Trends by Vehicle Type"
    )
    st.altair_chart(trend_chart, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Vehicle count trends
        count_trends = filtered_df.groupby(['Model Year', 'Electric Vehicle Type']).size().reset_index(name='Count')

        area_chart = alt.Chart(count_trends).mark_area().encode(
            x=alt.X('Model Year:O', title='Model Year'),
            y=alt.Y('Count:Q', title='Number of Vehicles'),
            color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='category20')),
            tooltip=['Model Year', 'Electric Vehicle Type', 'Count']
        ).properties(
            width=350,
            height=400,
            title="Vehicle Registration Trends"
        )
        st.altair_chart(area_chart, use_container_width=True)

    with col2:
        # Make diversity over time
        make_diversity = filtered_df.groupby('Model Year')['Make'].nunique().reset_index()
        make_diversity.columns = ['Model Year', 'Unique_Makes']

        diversity_chart = alt.Chart(make_diversity).mark_bar().encode(
            x=alt.X('Model Year:O', title='Model Year'),
            y=alt.Y('Unique_Makes:Q', title='Number of Unique Makes'),
            color=alt.Color('Unique_Makes:Q', scale=alt.Scale(scheme='viridis')),
            tooltip=['Model Year', 'Unique_Makes']
        ).properties(
            width=350,
            height=400,
            title="Make Diversity Over Time"
        )
        st.altair_chart(diversity_chart, use_container_width=True)


# Helper functions for calculations
def calculate_growth_rate(df):
    """Calculate year-over-year growth rate"""
    if 'Model Year' not in df.columns or len(df) < 2:
        return None

    yearly_counts = df.groupby('Model Year').size()
    if len(yearly_counts) < 2:
        return None

    latest_year = yearly_counts.index[-1]
    previous_year = yearly_counts.index[-2]

    if previous_year in yearly_counts.index and latest_year in yearly_counts.index:
        growth = ((yearly_counts[latest_year] - yearly_counts[previous_year]) / yearly_counts[previous_year]) * 100
        return growth
    return None


def calculate_price_trend(df):
    """Calculate price trend"""
    if 'Base MSRP' not in df.columns or 'Model Year' not in df.columns:
        return None

    yearly_prices = df.groupby('Model Year')['Base MSRP'].mean()
    if len(yearly_prices) < 2:
        return None

    return ((yearly_prices.iloc[-1] - yearly_prices.iloc[-2]) / yearly_prices.iloc[-2]) * 100


def calculate_range_trend(df):
    """Calculate range trend"""
    if 'Model Year' not in df.columns:
        return None

    yearly_ranges = df.groupby('Model Year')['Electric Range'].mean()
    if len(yearly_ranges) < 2:
        return None

    return ((yearly_ranges.iloc[-1] - yearly_ranges.iloc[-2]) / yearly_ranges.iloc[-2]) * 100


def calculate_market_concentration(df):
    """Calculate market concentration (HHI)"""
    if 'Make' not in df.columns:
        return 0

    market_shares = df['Make'].value_counts(normalize=True)
    hhi = (market_shares ** 2).sum() * 100
    return hhi


def calculate_range_improvement(df):
    """Calculate overall range improvement over time"""
    if 'Model Year' not in df.columns or len(df) < 2:
        return None

    yearly_avg = df.groupby('Model Year')['Electric Range'].mean()
    if len(yearly_avg) < 2:
        return None

    first_year_avg = yearly_avg.iloc[0]
    last_year_avg = yearly_avg.iloc[-1]

    return ((last_year_avg - first_year_avg) / first_year_avg) * 100


# Stub pages for remaining navigation
def leaders_page(filtered_df, display_df):
    """Market Leaders Analysis with comprehensive rankings"""
    st.markdown('<h1 class="main-header">Market Leaders Analysis</h1>', unsafe_allow_html=True)

    # Return to Home button
    if st.button("Return to Home", key="leaders_home", help="Go back to home page"):
        st.session_state.current_page = "Home"
        st.rerun()

    if filtered_df.empty:
        st.warning("No data available with current filters. Please adjust your selection.")
        return

    # Leadership metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        top_make = filtered_df['Make'].value_counts().index[0]
        top_make_count = filtered_df['Make'].value_counts().iloc[0]
        market_share = (top_make_count / len(filtered_df)) * 100
        st.metric("Market Leader", top_make, f"{market_share:.1f}% share")

    with col2:
        if 'Base MSRP' in filtered_df.columns:
            luxury_leader = filtered_df[filtered_df['Base MSRP'] > 80000]['Make'].value_counts()
            if not luxury_leader.empty:
                st.metric("Luxury Leader", luxury_leader.index[0], f"{luxury_leader.iloc[0]} vehicles")

    with col3:
        range_leader_data = filtered_df.loc[filtered_df['Electric Range'].idxmax()]
        st.metric("Range Leader", range_leader_data['Make'], f"{range_leader_data['Electric Range']:.0f} mi")

    with col4:
        fastest_growing = calculate_fastest_growing_make(filtered_df)
        if fastest_growing:
            st.metric("Fastest Growing", fastest_growing[0], f"+{fastest_growing[1]:.1f}%")

    # Main analysis charts
    col1, col2 = st.columns(2)

    with col1:
        # Market share ranking
        market_ranking = filtered_df['Make'].value_counts().head(10).reset_index()
        market_ranking.columns = ['Make', 'Count']
        market_ranking['Market_Share'] = (market_ranking['Count'] / len(filtered_df) * 100).round(1)

        ranking_chart = alt.Chart(market_ranking).mark_bar().encode(
            x=alt.X('Market_Share:Q', title='Market Share (%)'),
            y=alt.Y('Make:N', sort='-x', title='Vehicle Make'),
            color=alt.Color('Market_Share:Q', scale=alt.Scale(scheme='blues'), legend=None),
            tooltip=['Make', 'Count', alt.Tooltip('Market_Share:Q', format='.1f')]
        ).properties(
            width=350,
            height=400,
            title="Top 10 Market Share Leaders"
        )
        st.altair_chart(ranking_chart, use_container_width=True)

    with col2:
        # Performance vs Volume scatter
        make_performance = filtered_df.groupby('Make').agg({
            'Electric Range': 'mean',
            'Make': 'count'
        }).round(1)
        make_performance.columns = ['Avg_Range', 'Volume']
        make_performance = make_performance[make_performance['Volume'] >= 5].head(15).reset_index()

        perf_volume_chart = alt.Chart(make_performance).mark_circle(size=100).encode(
            x=alt.X('Volume:Q', title='Vehicle Volume'),
            y=alt.Y('Avg_Range:Q', title='Average Range (miles)'),
            size=alt.Size('Volume:Q', scale=alt.Scale(range=[100, 500]), legend=None),
            color=alt.Color('Make:N', scale=alt.Scale(scheme='category20'), legend=None),
            tooltip=['Make', 'Volume', alt.Tooltip('Avg_Range:Q', format='.1f')]
        ).properties(
            width=350,
            height=400,
            title="Performance vs Volume Matrix"
        )
        st.altair_chart(perf_volume_chart, use_container_width=True)

    # Detailed rankings
    st.markdown("### Detailed Market Rankings")

    col1, col2 = st.columns(2)

    with col1:
        # Volume leaders
        st.markdown("#### Volume Leaders")
        volume_leaders = filtered_df['Make'].value_counts().head(10).reset_index()
        volume_leaders.columns = ['Make', 'Vehicles']
        volume_leaders['Rank'] = range(1, len(volume_leaders) + 1)
        volume_leaders['Market Share'] = (volume_leaders['Vehicles'] / len(filtered_df) * 100).round(1)

        st.dataframe(
            volume_leaders[['Rank', 'Make', 'Vehicles', 'Market Share']],
            use_container_width=True,
            hide_index=True
        )

    with col2:
        # Performance leaders
        st.markdown("#### Range Performance Leaders")
        range_leaders = filtered_df.groupby('Make')['Electric Range'].agg(['mean', 'max', 'count']).round(1)
        range_leaders.columns = ['Avg Range', 'Max Range', 'Count']
        range_leaders = range_leaders[range_leaders['Count'] >= 3].sort_values('Avg Range', ascending=False).head(10)
        range_leaders['Rank'] = range(1, len(range_leaders) + 1)
        range_leaders = range_leaders.reset_index()

        st.dataframe(
            range_leaders[['Rank', 'Make', 'Avg Range', 'Max Range']],
            use_container_width=True,
            hide_index=True
        )

    # Price leadership analysis
    if 'Base MSRP' in filtered_df.columns:
        st.markdown("### Price Segment Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Premium segment leaders
            premium_data = filtered_df[filtered_df['Base MSRP'] > 60000]
            if not premium_data.empty:
                premium_leaders = premium_data['Make'].value_counts().head(8).reset_index()
                premium_leaders.columns = ['Make', 'Count']

                premium_chart = alt.Chart(premium_leaders).mark_arc().encode(
                    theta=alt.Theta('Count:Q'),
                    color=alt.Color('Make:N', scale=alt.Scale(scheme='category20')),
                    tooltip=['Make', 'Count']
                ).properties(
                    width=300,
                    height=300,
                    title="Premium Segment Leaders ($60K+)"
                )
                st.altair_chart(premium_chart, use_container_width=True)

        with col2:
            # Value segment leaders
            value_data = filtered_df[filtered_df['Base MSRP'] <= 45000]
            if not value_data.empty:
                value_leaders = value_data['Make'].value_counts().head(8).reset_index()
                value_leaders.columns = ['Make', 'Count']

                value_chart = alt.Chart(value_leaders).mark_arc().encode(
                    theta=alt.Theta('Count:Q'),
                    color=alt.Color('Make:N', scale=alt.Scale(scheme='set3')),
                    tooltip=['Make', 'Count']
                ).properties(
                    width=300,
                    height=300,
                    title="Value Segment Leaders ($45K-)"
                )
                st.altair_chart(value_chart, use_container_width=True)


def calculate_fastest_growing_make(df):
    """Calculate fastest growing make year over year"""
    if 'Model Year' not in df.columns or len(df) < 50:
        return None

    try:
        # Get last two years of data
        years = sorted(df['Model Year'].unique())
        if len(years) < 2:
            return None

        recent_year = years[-1]
        previous_year = years[-2]

        recent_counts = df[df['Model Year'] == recent_year]['Make'].value_counts()
        previous_counts = df[df['Model Year'] == previous_year]['Make'].value_counts()

        growth_rates = {}
        for make in recent_counts.index:
            if make in previous_counts.index and previous_counts[make] > 0:
                growth = ((recent_counts[make] - previous_counts[make]) / previous_counts[make]) * 100
                if recent_counts[make] >= 5:  # Minimum volume threshold
                    growth_rates[make] = growth

        if growth_rates:
            fastest = max(growth_rates.items(), key=lambda x: x[1])
            return fastest
        return None
    except:
        return None


# Main Application
def main():
    init_session_state()

    if st.session_state.df.empty:
        st.error("Unable to load data. Please check your dataset.")
        return

    # Create filters and get data (navigation is now included in sidebar)
    filtered_df, display_df = create_sidebar_filters()

    # Get current page from session state
    selected_page = st.session_state.current_page

    # Route to appropriate page
    if "Home" in selected_page:
        home_page()
    elif "Executive Dashboard" in selected_page:
        overview_page(filtered_df, display_df)
    elif "Price Analytics" in selected_page:
        price_page(filtered_df, display_df)
    elif "Geographic Insights" in selected_page:
        geographic_page(filtered_df, display_df)
    elif "Performance Analysis" in selected_page:
        performance_page(filtered_df, display_df)
    elif "Market Leaders" in selected_page:
        leaders_page(filtered_df, display_df)
    elif "Distribution Analysis" in selected_page:
        distribution_page(filtered_df, display_df)
    elif "Market Share" in selected_page:
        pie_page(filtered_df, display_df)
    elif "Box Analysis" in selected_page:
        boxplot_page(filtered_df, display_df)
    elif "Heatmap Analysis" in selected_page:
        heatmap_page(filtered_df, display_df)
    elif "Trends Analysis" in selected_page:
        trends_page(filtered_df, display_df)


if __name__ == "__main__":
    main()