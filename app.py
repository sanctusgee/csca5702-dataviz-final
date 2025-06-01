import streamlit as st
import pandas as pd
import altair as alt

# Set page configuration
st.set_page_config(page_title="EV Population Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/electric_vehicle_population.csv")
    df = df.dropna(subset=['Model Year', 'Make', 'Electric Vehicle Type', 'Electric Range'])
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
vehicle_types = df['Electric Vehicle Type'].unique().tolist()
selected_types = st.sidebar.multiselect("Select Vehicle Types:", vehicle_types, default=vehicle_types)

makes = df['Make'].unique().tolist()
selected_makes = st.sidebar.multiselect("Select Makes:", makes, default=makes)

# Filter data based on selections
filtered_df = df[(df['Electric Vehicle Type'].isin(selected_types)) & (df['Make'].isin(selected_makes))]

# Main dashboard
st.title("Electric Vehicle Population Dashboard")

# Histogram: Distribution of Electric Range
st.subheader("Distribution of Electric Range")
hist = alt.Chart(filtered_df).mark_bar().encode(
    alt.X("Electric Range:Q", bin=alt.Bin(maxbins=30), title="Electric Range (miles)"),
    y='count()',
    tooltip=['count()']
).properties(width=700, height=400)
st.altair_chart(hist, use_container_width=True)

# Boxplot: Electric Range by Vehicle Type
st.subheader("Electric Range by Vehicle Type")
box = alt.Chart(filtered_df).mark_boxplot().encode(
    x=alt.X('Electric Vehicle Type:N', title="Vehicle Type"),
    y=alt.Y('Electric Range:Q', title="Electric Range (miles)"),
    color='Electric Vehicle Type:N'
).properties(width=700, height=400)
st.altair_chart(box, use_container_width=True)

# Pie Chart: Distribution of Vehicle Types
st.subheader("Distribution of Vehicle Types")
type_counts = filtered_df['Electric Vehicle Type'].value_counts().reset_index()
type_counts.columns = ['Vehicle Type', 'Count']
pie = alt.Chart(type_counts).mark_arc().encode(
    theta=alt.Theta(field="Count", type="quantitative"),
    color=alt.Color(field="Vehicle Type", type="nominal"),
    tooltip=['Vehicle Type', 'Count']
).properties(width=700, height=400)
st.altair_chart(pie, use_container_width=True)

# Area Chart: Cumulative Vehicle Count Over Years
st.subheader("Cumulative Vehicle Count Over Years")
yearly_counts = filtered_df.groupby('Model Year').size().reset_index(name='Count')
yearly_counts['Cumulative Count'] = yearly_counts['Count'].cumsum()
area = alt.Chart(yearly_counts).mark_area().encode(
    x=alt.X('Model Year:O', title="Model Year"),
    y=alt.Y('Cumulative Count:Q', title="Cumulative Vehicle Count"),
    tooltip=['Model Year', 'Cumulative Count']
).properties(width=700, height=400)
st.altair_chart(area, use_container_width=True)

# Heatmap: Vehicle Count by Make and Model Year
st.subheader("Vehicle Count by Make and Model Year")
heatmap_data = filtered_df.groupby(['Make', 'Model Year']).size().reset_index(name='Count')
heatmap = alt.Chart(heatmap_data).mark_rect().encode(
    x=alt.X('Model Year:O', title="Model Year"),
    y=alt.Y('Make:N', title="Make"),
    color=alt.Color('Count:Q', scale=alt.Scale(scheme='viridis')),
    tooltip=['Make', 'Model Year', 'Count']
).properties(width=700, height=400)
st.altair_chart(heatmap, use_container_width=True)

# Scatter Plot: Electric Range vs. Model Year
st.subheader("Electric Range vs. Model Year")
scatter = alt.Chart(filtered_df).mark_circle(size=60).encode(
    x=alt.X('Model Year:O', title="Model Year"),
    y=alt.Y('Electric Range:Q', title="Electric Range (miles)"),
    color='Electric Vehicle Type:N',
    tooltip=['Make', 'Model Year', 'Electric Range']
).interactive().properties(width=700, height=400)
st.altair_chart(scatter, use_container_width=True)

# Faceted Line Charts: Electric Range Trends by Vehicle Type
st.subheader("Electric Range Trends by Vehicle Type")
line = alt.Chart(filtered_df).mark_line().encode(
    x=alt.X('Model Year:O', title="Model Year"),
    y=alt.Y('mean(Electric Range):Q', title="Average Electric Range"),
    color='Electric Vehicle Type:N'
).facet(
    column='Electric Vehicle Type:N'
).properties(width=200, height=200)
st.altair_chart(line, use_container_width=True)
