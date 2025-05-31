import pandas as pd
import altair as alt
import os

# Ensure output directories exist
os.makedirs('templates', exist_ok=True)
os.makedirs('docs', exist_ok=True)

# Load data
df = pd.read_csv('data/electric_vehicle_population.csv')
required_cols = ['Model Year', 'Make', 'Electric Vehicle Type', 'Electric Range']
df = df[required_cols].dropna()

# Use consistent color palette for accessibility
tableau_palette = 'tableau20'
viridis_palette = 'viridis'

# Grouped Bar Chart: Average Electric Range by Vehicle Type
avg_stats = (
    df.groupby('Electric Vehicle Type')['Electric Range']
    .mean()
    .reset_index()
    .rename(columns={'Electric Range': 'Avg Range'})
)

bar_chart = (
    alt.Chart(avg_stats)
    .mark_bar()
    .encode(
        x=alt.X('Electric Vehicle Type:N', title='Vehicle Type'),
        y=alt.Y('Avg Range:Q', title='Average Electric Range (miles)'),
        color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme=tableau_palette)),
        tooltip=[
            alt.Tooltip('Electric Vehicle Type:N', title='Vehicle Type'),
            alt.Tooltip('Avg Range:Q', format='.2f', title='Average Range (miles)')
        ]
    )
    .properties(
        title='Average Electric Range by Vehicle Type',
        width=600,
        height=400
    )
    .configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )
    .configure_title(
        fontSize=18,
        anchor='start'
    )
)
bar_chart.save('templates/average_stats_by_vehicle_type.html')
bar_chart.save('docs/average_stats_by_vehicle_type.html')

#2. Line Chart with Dropdown Filtering: Electric Range Trends Over Years
top_types = df['Electric Vehicle Type'].value_counts().head(5).index.tolist()
type_dropdown = alt.binding_select(
    options=top_types,
    name='Select Vehicle Type:'
)
type_select = alt.selection_point(
    fields=['Electric Vehicle Type'],
    bind=type_dropdown,
    value=[{'Electric Vehicle Type': top_types[0]}]
)

trend_chart = (
    alt.Chart(df)
    .mark_line(point=True)
    .encode(
        x=alt.X('Model Year:N', sort='ascending', title='Model Year'),
        y=alt.Y('Electric Range:Q', title='Electric Range (miles)'),
        color=alt.Color('Electric Vehicle Type:N', legend=None, scale=alt.Scale(scheme=tableau_palette)),
        tooltip=[
            alt.Tooltip('Model Year:N', title='Model Year'),
            alt.Tooltip('Make:N', title='Make'),
            alt.Tooltip('Electric Vehicle Type:N', title='Vehicle Type'),
            alt.Tooltip('Electric Range:Q', format='.2f', title='Range (miles)')
        ]
    )
    .add_params(type_select)
    .transform_filter(type_select)
    .properties(
        title='Electric Range Trends by Vehicle Type',
        width=700,
        height=400
    )
    .configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )
    .configure_title(
        fontSize=18,
        anchor='start'
    )
)
trend_chart.save('templates/electric_range_trends.html')
trend_chart.save('docs/electric_range_trends.html')

# 3. Leaderboard with Hover Brushing: Top Manufacturers by Vehicle Count
top_makes = (
    df['Make']
    .value_counts()
    .head(10)
    .reset_index(name='Vehicle Count')
    .rename(columns={'index': 'Make'})
)

highlight = alt.selection_point(
    on='mouseover',
    empty='none',
    fields=['Make']
)

leaderboard = (
    alt.Chart(top_makes)
    .mark_bar()
    .encode(
        y=alt.Y('Make:N', sort='-x', title='Manufacturer'),
        x=alt.X('Vehicle Count:Q', title='Number of Vehicles'),
        color=alt.condition(
            highlight,
            alt.Color('Vehicle Count:Q', scale=alt.Scale(scheme=viridis_palette)),
            alt.value('lightgray')
        ),
        tooltip=[
            alt.Tooltip('Make:N', title='Manufacturer'),
            alt.Tooltip('Vehicle Count:Q', format=',', title='Count')
        ]
    )
    .add_params(highlight)
    .properties(
        title='Top 10 Manufacturers by Vehicle Count',
        width=600,
        height=400
    )
    .configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )
    .configure_title(
        fontSize=18,
        anchor='start'
    )
)
leaderboard.save('templates/top_manufacturers.html')
leaderboard.save('docs/top_manufacturers.html')

print("Visualizations generated and saved!")
