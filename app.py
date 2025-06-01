import streamlit as st
import pandas as pd
import altair as alt

# Page Config
st.set_page_config(page_title="EV Dashboard: Interactive & Professional", layout="wide")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("data/electric_vehicle_population.csv")
    df = df.dropna(subset=['Model Year', 'Make', 'Electric Vehicle Type', 'Electric Range'])
    return df

df = load_data()

# Session State Initialization
if 'selected_makes' not in st.session_state:
    st.session_state.selected_makes = df['Make'].unique().tolist()
if 'selected_types' not in st.session_state:
    st.session_state.selected_types = df['Electric Vehicle Type'].unique().tolist()

# Sidebar: Dynamic Dropdowns
st.sidebar.header("Filter Options")

# Makes Dropdown with Select All
makes = sorted(df['Make'].unique().tolist())
select_all_makes = st.sidebar.checkbox("Select All Makes", value=True)
if select_all_makes:
    selected_makes = makes
else:
    selected_makes = st.sidebar.multiselect("Select Makes:", makes, default=st.session_state.selected_makes)
st.session_state.selected_makes = selected_makes

# Vehicle Types Dropdown with Select All
vehicle_types = sorted(df['Electric Vehicle Type'].unique().tolist())
select_all_types = st.sidebar.checkbox("Select All Vehicle Types", value=True)
if select_all_types:
    selected_types = vehicle_types
else:
    selected_types = st.sidebar.multiselect("Select Vehicle Types:", vehicle_types, default=st.session_state.selected_types)
st.session_state.selected_types = selected_types

# Filter Data
filtered_df = df[
    (df['Make'].isin(selected_makes)) &
    (df['Electric Vehicle Type'].isin(selected_types))
]

# Show Record Count
total_records = filtered_df.shape[0]
st.sidebar.markdown(f"**Filtered Records:** {total_records:,}")

# Toggle Sample Mode
use_sample = st.sidebar.checkbox("Use Sample Mode (5,000 Points)", value=True)

if use_sample and total_records > 5000:
    display_df = filtered_df.sample(n=5000, random_state=42)
    st.sidebar.warning(f"Sample Mode: Displaying a random 5,000 records out of {total_records:,} total.")
else:
    display_df = filtered_df
    st.sidebar.info(f"Displaying all {total_records:,} records.")

# Title
st.title("Electric Vehicle Population Dashboard with Advanced Visuals")

# Notify user if sampling is active
if use_sample and total_records > 5000:
    st.warning(f"Sample Mode is active — showing 5,000 points out of {total_records:,}. Use filters to refine.")

# Color Scales
color_vehicle_type = alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='category20'))
color_make = alt.Color('Make:N', scale=alt.Scale(scheme='category20'))

# Selection for Interactivity
vehicle_type_selection = alt.selection_point(fields=['Electric Vehicle Type'])

# 1️⃣ Bar Chart: Vehicles by Type
bar_chart = alt.Chart(filtered_df).mark_bar().encode(
    x=alt.X('Electric Vehicle Type:N', title='Vehicle Type'),
    y=alt.Y('count()', title='Number of Vehicles'),
    color=color_vehicle_type,
    tooltip=['Electric Vehicle Type', 'count()']
).add_params(
    vehicle_type_selection
).properties(
    width=700,
    height=400,
    title="Click a Vehicle Type to Filter Other Charts"
)
st.altair_chart(bar_chart, use_container_width=True)

# 2️⃣ Scatter Plot: Range vs. Year
scatter_plot = alt.Chart(display_df).mark_circle(size=60).encode(
    x=alt.X('Model Year:O', title='Model Year'),
    y=alt.Y('Electric Range:Q', title='Electric Range (miles)'),
    color=color_make,
    tooltip=['Make', 'Model Year', 'Electric Vehicle Type', 'Electric Range']
).transform_filter(
    vehicle_type_selection
).interactive().properties(
    width=700,
    height=400,
    title='Electric Range vs. Model Year'
)
st.altair_chart(scatter_plot, use_container_width=True)

# 3️⃣ Boxplot: Range by Vehicle Type
top_types = filtered_df['Electric Vehicle Type'].value_counts().head(5).index.tolist()
filtered_box_df = filtered_df[filtered_df['Electric Vehicle Type'].isin(top_types)]
boxplot = alt.Chart(filtered_box_df).mark_boxplot().encode(
    x=alt.X('Electric Vehicle Type:N', title='Vehicle Type'),
    y=alt.Y('Electric Range:Q', title='Electric Range (miles)'),
    color=color_vehicle_type
).transform_filter(
    vehicle_type_selection
).properties(
    width=700,
    height=400,
    title='Electric Range by Vehicle Type'
)
st.altair_chart(boxplot, use_container_width=True)

# 4️⃣ Heatmap: Vehicle Count by Make and Year
heatmap_data = (
    filtered_df
    .groupby(['Make', 'Model Year'])
    .size()
    .reset_index(name='Count')
)
heatmap = alt.Chart(heatmap_data).mark_rect().encode(
    x=alt.X('Model Year:O', title='Model Year'),
    y=alt.Y('Make:N', title='Make'),
    color=alt.Color('Count:Q', scale=alt.Scale(scheme='viridis')),
    tooltip=['Make', 'Model Year', 'Count']
).properties(
    width=700,
    height=400,
    title='Vehicle Count by Make and Year'
)
st.altair_chart(heatmap, use_container_width=True)

# 5️⃣ Histogram: Electric Range Distribution
histogram = alt.Chart(display_df).mark_bar().encode(
    x=alt.X('Electric Range:Q', bin=alt.Bin(maxbins=40), title='Electric Range (miles)'),
    y=alt.Y('count()', title='Number of Vehicles'),
    color=color_vehicle_type,
    tooltip=['count()']
).properties(
    width=700,
    height=400,
    title='Distribution of Electric Range'
)
st.altair_chart(histogram, use_container_width=True)

# 6️⃣ Pie Chart: Market Share by Vehicle Type
pie_data = (
    filtered_df
    .groupby('Electric Vehicle Type')
    .size()
    .reset_index(name='Count')
)
pie_chart = alt.Chart(pie_data).mark_arc().encode(
    theta=alt.Theta('Count:Q', stack=True),
    color=color_vehicle_type,
    tooltip=['Electric Vehicle Type', 'Count']
).properties(
    width=400,
    height=400,
    title='Market Share by Vehicle Type'
)
st.altair_chart(pie_chart, use_container_width=False)

# 7️⃣ Line Chart: Average Electric Range by Year and Vehicle Type
range_trends = (
    filtered_df
    .groupby(['Model Year', 'Electric Vehicle Type'])
    .agg({'Electric Range': 'mean'})
    .reset_index()
)
line_chart = alt.Chart(range_trends).mark_line(point=True).encode(
    x=alt.X('Model Year:O', title='Model Year'),
    y=alt.Y('Electric Range:Q', title='Average Electric Range (miles)'),
    color=color_vehicle_type,
    tooltip=['Model Year', 'Electric Vehicle Type', alt.Tooltip('Electric Range:Q', format='.2f')]
).transform_filter(
    vehicle_type_selection
).properties(
    width=700,
    height=400,
    title='Average Electric Range Trends by Vehicle Type'
)
st.altair_chart(line_chart, use_container_width=True)
