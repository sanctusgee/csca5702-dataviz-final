import streamlit as st
import pandas as pd
import altair as alt

# Page Config
st.set_page_config(page_title="EV Dashboard with Session State", layout="wide")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("data/electric_vehicle_population.csv")
    df = df.dropna(subset=['Model Year', 'Make', 'Electric Vehicle Type', 'Electric Range'])
    return df

df = load_data()

# Initialize session state
if 'selected_makes' not in st.session_state:
    st.session_state.selected_makes = df['Make'].unique().tolist()

if 'selected_types' not in st.session_state:
    st.session_state.selected_types = df['Electric Vehicle Type'].unique().tolist()

# Sidebar Filters
st.sidebar.header("Filters")

# Dynamic dropdowns based on bar chart selection
makes = df['Make'].unique().tolist()
selected_makes = st.sidebar.multiselect(
    "Select Makes:", makes,
    default=st.session_state.selected_makes
)

# Update session state
st.session_state.selected_makes = selected_makes

vehicle_types = df['Electric Vehicle Type'].unique().tolist()
selected_types = st.sidebar.multiselect(
    "Select Vehicle Types:",
    vehicle_types,
    default=st.session_state.selected_types
)

st.session_state.selected_types = selected_types

filtered_df = df[
    (df['Make'].isin(selected_makes)) &
    (df['Electric Vehicle Type'].isin(selected_types))
]

# Show filtered record count
total_records = filtered_df.shape[0]
st.sidebar.markdown(f"Filtered Records: {total_records:,}")

# Toggle Sample Mode
use_sample = st.sidebar.checkbox("Use Sample Mode (5,000 Points)", value=True)

if use_sample and total_records > 5000:
    display_df = filtered_df.sample(n=5000, random_state=42)
    st.sidebar.markdown("Displaying a random sample of 5,000 records.")
else:
    display_df = filtered_df
    st.sidebar.markdown(f"Displaying all {total_records:,} records.")

st.title("Electric Vehicle Dashboard with Session State and Dynamic Dropdowns")

# Selection Object for Linking
vehicle_type_selection = alt.selection_point(fields=['Electric Vehicle Type'])

# 1. Bar Chart for Vehicle Type Selection
bar = alt.Chart(filtered_df).mark_bar().encode(
    x=alt.X('Electric Vehicle Type:N', title="Vehicle Type"),
    y=alt.Y('count()', title="Number of Vehicles"),
    color=alt.condition(vehicle_type_selection, alt.Color('Electric Vehicle Type:N', legend=None), alt.value('lightgray')),
    tooltip=['Electric Vehicle Type', 'count()']
).add_params(
    vehicle_type_selection
).properties(width=700, height=400, title="Click a Vehicle Type to Filter Other Charts")

st.altair_chart(bar, use_container_width=True)

# 2. Update Vehicle Type Dropdown Based on Selection
selected_points = vehicle_type_selection.resolve_selection(filtered_df)
if selected_points:
    selected_vehicle_types = list(set(point['Electric Vehicle Type'] for point in selected_points))
    st.session_state.selected_types = selected_vehicle_types

# 3. Scatter Plot with Sampling
scatter = alt.Chart(display_df).mark_circle(size=60).encode(
    x=alt.X('Model Year:O', title="Model Year"),
    y=alt.Y('Electric Range:Q', title="Electric Range (miles)"),
    color=alt.Color('Electric Vehicle Type:N'),
    tooltip=['Make', 'Model Year', 'Electric Vehicle Type', 'Electric Range']
).transform_filter(
    vehicle_type_selection
).interactive().properties(width=700, height=400, title="Electric Range vs. Model Year")

st.altair_chart(scatter, use_container_width=True)

# 4. Boxplot (Top 5 Vehicle Types)
top_types = (
    filtered_df['Electric Vehicle Type']
    .value_counts()
    .head(5)
    .index
    .tolist()
)
filtered_box_df = filtered_df[filtered_df['Electric Vehicle Type'].isin(top_types)]
box = alt.Chart(filtered_box_df).mark_boxplot().encode(
    x=alt.X('Electric Vehicle Type:N', title="Vehicle Type"),
    y=alt.Y('Electric Range:Q', title="Electric Range (miles)"),
    color='Electric Vehicle Type:N'
).transform_filter(
    vehicle_type_selection
).properties(width=700, height=400, title="Range by Vehicle Type (Filtered)")

st.altair_chart(box, use_container_width=True)

# 5. Heatmap with Pre-aggregation
top_makes_heatmap = (
    filtered_df['Make']
    .value_counts()
    .head(10)
    .index
    .tolist()
)
heatmap_data = (
    filtered_df[filtered_df['Make'].isin(top_makes_heatmap)]
    .groupby(['Make', 'Model Year'])
    .size()
    .reset_index(name='Count')
)
heatmap = alt.Chart(heatmap_data).mark_rect().encode(
    x=alt.X('Model Year:O', title="Model Year"),
    y=alt.Y('Make:N', title="Make"),
    color=alt.Color('Count:Q', scale=alt.Scale(scheme='viridis')),
    tooltip=['Make', 'Model Year', 'Count']
).transform_filter(
    vehicle_type_selection
).properties(width=700, height=400, title="Vehicle Count by Make and Year (Filtered)")

st.altair_chart(heatmap, use_container_width=True)
