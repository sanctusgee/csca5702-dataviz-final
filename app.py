import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="WA State EV Analytics Platform",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
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
    if 'year_range' not in st.session_state:
        min_year = int(st.session_state.df['Model Year'].min())
        max_year = int(st.session_state.df['Model Year'].max())
        st.session_state.year_range = (min_year, max_year)
    if 'price_range' not in st.session_state and 'Base MSRP' in st.session_state.df.columns:
        min_price = int(st.session_state.df['Base MSRP'].min())
        max_price = int(st.session_state.df['Base MSRP'].max())
        st.session_state.price_range = (min_price, max_price)


# Advanced Sidebar Filtering
def create_sidebar_filters():
    """Create comprehensive sidebar filters"""
    if st.session_state.df.empty:
        return None, None

    st.sidebar.markdown("### Advanced Filter Controls")

    # Year Range Slider
    min_year = int(st.session_state.df['Model Year'].min())
    max_year = int(st.session_state.df['Model Year'].max())
    year_range = st.sidebar.slider(
        "Model Year Range",
        min_year, max_year,
        st.session_state.year_range,
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
            min_price, max_price,
            st.session_state.price_range,
            format="$%d",
            key="price_slider"
        )
        st.session_state.price_range = price_filter

    # Geographic Filters
    if 'County' in st.session_state.df.columns:
        st.sidebar.markdown("#### Geographic Filters")
        counties = sorted(st.session_state.df['County'].dropna().unique().tolist())

        col1, col2 = st.sidebar.columns(2)
        with col1:
            select_all_counties = st.checkbox("All Counties", value=True, key="select_all_counties")
        with col2:
            clear_counties = st.button("Clear", key="clear_counties")

        if select_all_counties:
            st.session_state.selected_counties = counties
        elif clear_counties:
            st.session_state.selected_counties = []

        selected_counties = st.sidebar.multiselect(
            "Select Counties:",
            counties,
            default=st.session_state.selected_counties,
            key="counties_multiselect"
        )
        st.session_state.selected_counties = selected_counties

    # Makes Selection
    st.sidebar.markdown("#### Vehicle Makes")
    makes = sorted(st.session_state.df['Make'].unique().tolist())

    col1, col2 = st.sidebar.columns(2)
    with col1:
        select_all_makes = st.checkbox("All Makes", value=len(st.session_state.selected_makes) == len(makes),
                                       key="select_all_makes")
    with col2:
        clear_makes = st.button("Clear", key="clear_makes")

    if select_all_makes:
        st.session_state.selected_makes = makes
    elif clear_makes:
        st.session_state.selected_makes = []

    selected_makes = st.sidebar.multiselect(
        "Choose Makes:",
        makes,
        default=st.session_state.selected_makes,
        key="makes_multiselect"
    )
    st.session_state.selected_makes = selected_makes

    # Vehicle Types Selection
    st.sidebar.markdown("#### Vehicle Types")
    vehicle_types = sorted(st.session_state.df['Electric Vehicle Type'].unique().tolist())

    col1, col2 = st.sidebar.columns(2)
    with col1:
        select_all_types = st.checkbox("All Types", value=len(st.session_state.selected_types) == len(vehicle_types),
                                       key="select_all_types")
    with col2:
        clear_types = st.button("Clear", key="clear_types")

    if select_all_types:
        st.session_state.selected_types = vehicle_types
    elif clear_types:
        st.session_state.selected_types = []

    selected_types = st.sidebar.multiselect(
        "Choose Types:",
        vehicle_types,
        default=st.session_state.selected_types,
        key="types_multiselect"
    )
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
        min_range, max_range,
        (min_range, max_range),
        key="range_slider"
    )

    # Apply all filters
    filtered_df = st.session_state.df[
        (st.session_state.df['Make'].isin(selected_makes)) &
        (st.session_state.df['Electric Vehicle Type'].isin(selected_types)) &
        (st.session_state.df['Model Year'] >= year_range[0]) &
        (st.session_state.df['Model Year'] <= year_range[1]) &
        (st.session_state.df['Electric Range'] >= range_filter[0]) &
        (st.session_state.df['Electric Range'] <= range_filter[1])
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
    use_sample = st.sidebar.checkbox("Sample Mode (10,000 points)", value=True, key="sample_mode")

    total_records = len(filtered_df)
    if use_sample and total_records > 10000:
        display_df = filtered_df.sample(n=10000, random_state=42)
        st.sidebar.warning(f"Showing 10,000 of {total_records:,} records")
    else:
        display_df = filtered_df
        st.sidebar.success(f"Showing all {total_records:,} records")

    # Dataset Info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Real-Time Analytics")
    if not filtered_df.empty:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Total Vehicles", f"{total_records:,}")
            if 'Base MSRP' in filtered_df.columns:
                avg_price = filtered_df['Base MSRP'].mean()
                st.metric("Avg Price", f"${avg_price:,.0f}")
        with col2:
            avg_range = filtered_df['Electric Range'].mean()
            st.metric("Avg Range", f"{avg_range:.0f} mi")
            if 'County' in filtered_df.columns:
                unique_counties = filtered_df['County'].nunique()
                st.metric("Counties", f"{unique_counties}")

    return filtered_df, display_df


# Page Navigation
def create_navigation():
    """Create enhanced page navigation"""
    pages = {
        "Home": "home",
        "Executive Dashboard": "overview",
        "Price Analytics": "price",
        "Geographic Insights": "geographic",
        "Performance Analysis": "performance",
        "Market Leaders": "leaders",
        "Policy Impact": "policy",
        "Model Deep Dive": "models",
        "Utility Analysis": "utilities",
        "Advanced Analytics": "advanced"
    }

    return st.sidebar.selectbox("Navigate to Section", list(pages.keys()), key="navigation")


# Color Schemes
def get_color_schemes():
    """Define professional color schemes"""
    return {
        'categorical': px.colors.qualitative.Set3,
        'sequential': px.colors.sequential.Viridis,
        'diverging': px.colors.diverging.RdYlBu,
        'makes': px.colors.qualitative.Pastel,
        'types': px.colors.qualitative.Bold,
        'price': px.colors.sequential.Plasma,
        'geographic': px.colors.sequential.Blues,
        'performance': px.colors.sequential.Turbo
    }


# Individual Page Functions
def home_page():
    """Enhanced landing page with comprehensive overview"""
    st.markdown('<h1 class="main-header">Washington State EV Analytics Platform</h1>', unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: center; font-size: 1.3rem; color: #666; margin-bottom: 3rem;'>
        Advanced analytics platform for Washington State's electric vehicle ecosystem<br>
        <em>Data source: Washington State Department of Licensing</em>
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

    # Navigation guide
    st.markdown('<h2 class="sub-header">Explore Advanced Analytics</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Price Analytics**
        - MSRP vs Range performance analysis
        - Affordability trends by region
        - Value proposition insights

        **Geographic Insights** 
        - County-level adoption patterns
        - Urban vs rural preferences
        - Regional market characteristics

        **Performance Analysis**
        - Range distribution analysis
        - Technology advancement trends
        - Efficiency improvements

        **Market Leaders**
        - Brand performance rankings
        - Model popularity analysis
        - Competitive landscape
        """)

    with col2:
        st.markdown("""
        **Policy Impact**
        - CAFV eligibility analysis
        - Legislative district patterns
        - Incentive effectiveness

        **Model Deep Dive**
        - Specific model analytics
        - Feature comparison
        - Consumer preferences

        **Utility Analysis**
        - Electric utility territories
        - Infrastructure correlation
        - Service area insights

        **Advanced Analytics**
        - Multi-dimensional analysis
        - Predictive insights
        - Market forecasting
        """)


def overview_page(filtered_df, display_df):
    """Executive dashboard with comprehensive KPIs"""
    st.markdown('<h1 class="main-header">Executive Dashboard</h1>', unsafe_allow_html=True)

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
            fig_trends = px.area(
                yearly_trends,
                x='Model Year',
                y='Count',
                color='Electric Vehicle Type',
                color_discrete_sequence=get_color_schemes()['categorical'],
                title="Market Evolution by Vehicle Type"
            )
            fig_trends.update_layout(height=400)
            st.plotly_chart(fig_trends, use_container_width=True)

    with col2:
        # Price vs Performance scatter
        if 'Base MSRP' in filtered_df.columns:
            fig_scatter = px.scatter(
                display_df,
                x='Electric Range',
                y='Base MSRP',
                color='Electric Vehicle Type',
                size='Model Year',
                hover_data=['Make', 'Model'],
                color_discrete_sequence=get_color_schemes()['types'],
                title="Price vs Performance Matrix",
                opacity=0.7
            )
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)

    # Geographic and competitive analysis
    col1, col2 = st.columns(2)

    with col1:
        # Top performing counties
        if 'County' in filtered_df.columns:
            county_adoption = filtered_df['County'].value_counts().head(10).reset_index()
            county_adoption.columns = ['County', 'Count']

            fig_counties = px.bar(
                county_adoption,
                x='Count',
                y='County',
                orientation='h',
                color='Count',
                color_continuous_scale='Viridis',
                title="Top Counties by EV Adoption"
            )
            fig_counties.update_layout(height=400)
            st.plotly_chart(fig_counties, use_container_width=True)

    with col2:
        # Brand market share
        brand_share = filtered_df['Make'].value_counts().head(8).reset_index()
        brand_share.columns = ['Make', 'Count']
        brand_share['Percentage'] = (brand_share['Count'] / brand_share['Count'].sum() * 100).round(1)

        fig_brands = px.pie(
            brand_share,
            values='Count',
            names='Make',
            color_discrete_sequence=get_color_schemes()['makes'],
            title="Brand Market Share (Top 8)"
        )
        fig_brands.update_traces(textposition='inside', textinfo='percent+label')
        fig_brands.update_layout(height=400)
        st.plotly_chart(fig_brands, use_container_width=True)


def price_page(filtered_df, display_df):
    """Advanced price analytics page"""
    st.markdown('<h1 class="main-header">Price Analytics Dashboard</h1>', unsafe_allow_html=True)

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
        fig_price_dist = px.histogram(
            filtered_df,
            x='Base MSRP',
            color='Electric Vehicle Type',
            nbins=30,
            color_discrete_sequence=get_color_schemes()['types'],
            title="Price Distribution by Vehicle Type"
        )
        fig_price_dist.update_layout(height=400)
        st.plotly_chart(fig_price_dist, use_container_width=True)

    with col2:
        # Price vs Range efficiency
        filtered_df['Price_per_Mile'] = filtered_df['Base MSRP'] / filtered_df['Electric Range']
        efficiency_data = filtered_df.groupby('Make')['Price_per_Mile'].mean().sort_values().head(10).reset_index()

        fig_efficiency = px.bar(
            efficiency_data,
            x='Price_per_Mile',
            y='Make',
            orientation='h',
            color='Price_per_Mile',
            color_continuous_scale='RdYlGn_r',
            title="Price Efficiency ($/mile range)"
        )
        fig_efficiency.update_layout(height=400)
        st.plotly_chart(fig_efficiency, use_container_width=True)

    # Advanced price analysis
    col1, col2 = st.columns(2)

    with col1:
        # Price trends over time
        price_trends = filtered_df.groupby(['Model Year', 'Electric Vehicle Type'])['Base MSRP'].mean().reset_index()

        fig_price_trends = px.line(
            price_trends,
            x='Model Year',
            y='Base MSRP',
            color='Electric Vehicle Type',
            color_discrete_sequence=get_color_schemes()['categorical'],
            title="Average Price Trends Over Time",
            markers=True
        )
        fig_price_trends.update_layout(height=400)
        st.plotly_chart(fig_price_trends, use_container_width=True)

    with col2:
        # Price categories pie chart
        if 'Price_Category' in filtered_df.columns:
            price_cat_dist = filtered_df['Price_Category'].value_counts().reset_index()
            price_cat_dist.columns = ['Category', 'Count']

            fig_price_cat = px.pie(
                price_cat_dist,
                values='Count',
                names='Category',
                color_discrete_sequence=get_color_schemes()['price'],
                title="Market Segmentation by Price"
            )
            fig_price_cat.update_traces(textposition='inside', textinfo='percent+label')
            fig_price_cat.update_layout(height=400)
            st.plotly_chart(fig_price_cat, use_container_width=True)

    # Geographic price analysis
    if 'County' in filtered_df.columns:
        st.markdown("### Geographic Price Analysis")

        county_price_analysis = filtered_df.groupby('County').agg({
            'Base MSRP': ['mean', 'median', 'count']
        }).round(0)
        county_price_analysis.columns = ['Avg_Price', 'Median_Price', 'Vehicle_Count']
        county_price_analysis = county_price_analysis[county_price_analysis['Vehicle_Count'] >= 10].sort_values(
            'Avg_Price', ascending=False).head(15)

        fig_county_prices = px.bar(
            county_price_analysis.reset_index(),
            x='County',
            y='Avg_Price',
            color='Median_Price',
            color_continuous_scale='Viridis',
            title="Average Vehicle Prices by County (Top 15)"
        )
        fig_county_prices.update_layout(height=400)
        fig_county_prices.update_xaxes(tickangle=45)
        st.plotly_chart(fig_county_prices, use_container_width=True)


def geographic_page(filtered_df, display_df):
    """Geographic insights and analysis"""
    st.markdown('<h1 class="main-header">Geographic Market Insights</h1>', unsafe_allow_html=True)

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

        fig_counties = px.bar(
            county_counts,
            x='Count',
            y='County',
            orientation='h',
            color='Count',
            color_continuous_scale='Blues',
            title="Top 15 Counties by EV Adoption"
        )
        fig_counties.update_layout(height=500)
        st.plotly_chart(fig_counties, use_container_width=True)

    with col2:
        # Vehicle type distribution by top counties
        top_counties = filtered_df['County'].value_counts().head(8).index
        county_type_data = filtered_df[filtered_df['County'].isin(top_counties)]
        county_type_dist = county_type_data.groupby(['County', 'Electric Vehicle Type']).size().reset_index(
            name='Count')

        fig_county_types = px.bar(
            county_type_dist,
            x='County',
            y='Count',
            color='Electric Vehicle Type',
            color_discrete_sequence=get_color_schemes()['types'],
            title="Vehicle Types by Top Counties"
        )
        fig_county_types.update_layout(height=500)
        fig_county_types.update_xaxes(tickangle=45)
        st.plotly_chart(fig_county_types, use_container_width=True)

    # Urban vs Rural analysis
    if 'City' in filtered_df.columns:
        col1, col2 = st.columns(2)

        with col1:
            # Top cities
            city_counts = filtered_df['City'].value_counts().head(12).reset_index()
            city_counts.columns = ['City', 'Count']

            fig_cities = px.treemap(
                city_counts,
                path=['City'],
                values='Count',
                color='Count',
                color_continuous_scale='Greens',
                title="Top Cities by EV Adoption"
            )
            fig_cities.update_layout(height=400)
            st.plotly_chart(fig_cities, use_container_width=True)

        with col2:
            # City vs County comparison
            city_county_data = filtered_df.groupby(['County', 'City']).size().reset_index(name='Count')
            city_county_data = city_county_data.sort_values('Count', ascending=False).head(15)

            fig_city_county = px.scatter(
                city_county_data,
                x='Count',
                y='City',
                color='County',
                size='Count',
                color_discrete_sequence=get_color_schemes()['categorical'],
                title="City-County EV Distribution"
            )
            fig_city_county.update_layout(height=400)
            st.plotly_chart(fig_city_county, use_container_width=True)

    # Price and range analysis by geography
    if 'Base MSRP' in filtered_df.columns:
        st.markdown("### Geographic Economic Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Average prices by county
            county_price_data = filtered_df.groupby('County').agg({
                'Base MSRP': 'mean',
                'Electric Range': 'mean'
            }).reset_index()
            county_price_data = county_price_data.sort_values('Base MSRP', ascending=False).head(12)

            fig_county_prices = px.scatter(
                county_price_data,
                x='Electric Range',
                y='Base MSRP',
                size='Base MSRP',
                color='County',
                color_discrete_sequence=get_color_schemes()['makes'],
                title="County Price vs Range Profile"
            )
            fig_county_prices.update_layout(height=400)
            st.plotly_chart(fig_county_prices, use_container_width=True)

        with col2:
            # Affordability index by county
            county_affordability = filtered_df.groupby('County').agg({
                'Base MSRP': ['mean', lambda x: (x < 35000).mean() * 100]
            }).round(1)
            county_affordability.columns = ['Avg_Price', 'Affordable_Percent']
            county_affordability = county_affordability.reset_index().sort_values('Affordable_Percent',
                                                                                  ascending=False).head(12)

            fig_affordability = px.bar(
                county_affordability,
                x='Affordable_Percent',
                y='County',
                orientation='h',
                color='Affordable_Percent',
                color_continuous_scale='RdYlGn',
                title="Affordability Index by County (%<$35K)"
            )
            fig_affordability.update_layout(height=400)
            st.plotly_chart(fig_affordability, use_container_width=True)


def performance_page(filtered_df, display_df):
    """Performance and range analysis"""
    st.markdown('<h1 class="main-header">Performance Analytics</h1>', unsafe_allow_html=True)

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
        # Range distribution by type
        fig_range_dist = px.violin(
            display_df,
            y='Electric Range',
            x='Electric Vehicle Type',
            color='Electric Vehicle Type',
            color_discrete_sequence=get_color_schemes()['types'],
            title="Range Distribution by Vehicle Type",
            box=True
        )
        fig_range_dist.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_range_dist, use_container_width=True)

    with col2:
        # Range categories
        if 'Range_Category' in filtered_df.columns:
            range_cat_dist = filtered_df['Range_Category'].value_counts().reset_index()
            range_cat_dist.columns = ['Category', 'Count']

            fig_range_cat = px.pie(
                range_cat_dist,
                values='Count',
                names='Category',
                color_discrete_sequence=get_color_schemes()['performance'],
                title="Range Category Distribution"
            )
            fig_range_cat.update_traces(textposition='inside', textinfo='percent+label')
            fig_range_cat.update_layout(height=400)
            st.plotly_chart(fig_range_cat, use_container_width=True)

    # Performance trends
    col1, col2 = st.columns(2)

    with col1:
        # Range evolution over time
        range_trends = filtered_df.groupby(['Model Year', 'Electric Vehicle Type'])[
            'Electric Range'].mean().reset_index()

        fig_range_trends = px.line(
            range_trends,
            x='Model Year',
            y='Electric Range',
            color='Electric Vehicle Type',
            color_discrete_sequence=get_color_schemes()['categorical'],
            title="Range Evolution by Vehicle Type",
            markers=True
        )
        fig_range_trends.update_layout(height=400)
        st.plotly_chart(fig_range_trends, use_container_width=True)

    with col2:
        # Top performers by make
        make_performance = filtered_df.groupby('Make').agg({
            'Electric Range': ['mean', 'max', 'count']
        }).round(1)
        make_performance.columns = ['Avg_Range', 'Max_Range', 'Count']
        make_performance = make_performance[make_performance['Count'] >= 5].sort_values('Avg_Range',
                                                                                        ascending=False).head(10)

        fig_make_performance = px.scatter(
            make_performance.reset_index(),
            x='Avg_Range',
            y='Max_Range',
            size='Count',
            color='Make',
            color_discrete_sequence=get_color_schemes()['makes'],
            title="Make Performance Matrix",
            hover_data=['Count']
        )
        fig_make_performance.update_layout(height=400)
        st.plotly_chart(fig_make_performance, use_container_width=True)

    # Advanced performance analysis
    st.markdown("### Advanced Performance Insights")

    col1, col2 = st.columns(2)

    with col1:
        # Range improvement by model year
        yearly_stats = filtered_df.groupby('Model Year')['Electric Range'].agg(['mean', 'median', 'std']).round(1)
        yearly_stats = yearly_stats.reset_index()

        fig_yearly_performance = px.line(
            yearly_stats,
            x='Model Year',
            y=['mean', 'median'],
            title="Yearly Range Statistics",
            markers=True
        )
        fig_yearly_performance.update_layout(height=400)
        st.plotly_chart(fig_yearly_performance, use_container_width=True)

    with col2:
        # Performance leaders table
        performance_leaders = filtered_df.nlargest(10, 'Electric Range')[
            ['Make', 'Model', 'Model Year', 'Electric Range', 'Electric Vehicle Type']
        ]

        st.markdown("#### Top 10 Performance Leaders")
        st.dataframe(
            performance_leaders,
            use_container_width=True,
            hide_index=True
        )


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


# Additional page stubs for the remaining navigation items
def leaders_page(filtered_df, display_df):
    st.markdown('<h1 class="main-header">Market Leaders Analysis</h1>', unsafe_allow_html=True)
    st.info("Market leaders analysis - detailed rankings and competitive insights")


def policy_page(filtered_df, display_df):
    st.markdown('<h1 class="main-header">Policy Impact Analysis</h1>', unsafe_allow_html=True)
    st.info("CAFV eligibility and policy impact analysis")


def models_page(filtered_df, display_df):
    st.markdown('<h1 class="main-header">Model Deep Dive</h1>', unsafe_allow_html=True)
    st.info("Individual model performance and comparison analysis")


def utilities_page(filtered_df, display_df):
    st.markdown('<h1 class="main-header">Utility Territory Analysis</h1>', unsafe_allow_html=True)
    st.info("Electric utility correlation and infrastructure analysis")


def advanced_page(filtered_df, display_df):
    st.markdown('<h1 class="main-header">Advanced Analytics</h1>', unsafe_allow_html=True)
    st.info("Multi-dimensional analysis and predictive insights")


# Main Application
def main():
    init_session_state()

    if st.session_state.df.empty:
        st.error("Unable to load data. Please check your dataset.")
        return

    # Create filters and get data
    filtered_df, display_df = create_sidebar_filters()

    # Navigation
    selected_page = create_navigation()

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
    elif "Policy Impact" in selected_page:
        policy_page(filtered_df, display_df)
    elif "Model Deep Dive" in selected_page:
        models_page(filtered_df, display_df)
    elif "Utility Analysis" in selected_page:
        utilities_page(filtered_df, display_df)
    elif "Advanced Analytics" in selected_page:
        advanced_page(filtered_df, display_df)


if __name__ == "__main__":
    main()