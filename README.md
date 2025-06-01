# Washington State EV Analytics Platform

An interactive data visualization platform for exploring Washington State's electric vehicle population data, built with Streamlit and Altair for CSCA 5702 - Fundamentals of Data Visualization.

## Live Demo

**[View Live Application](https://csca5702-final-project.streamlit.app/)**

## Features

### Interactive Analytics Dashboard
- **11 Specialized Analysis Pages** covering market trends, pricing, geographic distribution, and performance metrics
- **Advanced Filtering System** with real-time updates across year ranges, price brackets, vehicle makes, types, and counties
- **Cross-Chart Interactivity** - click on any chart element to filter all related visualizations
- **UI/UX with gradient styling**, hover effects, and modern design patterns

### Key Visualizations
- Executive Dashboard with comprehensive KPIs and cross-filtering
- Price Analytics with cost trends and efficiency analysis
- Geographic Insights showing location-based adoption patterns
- Market Leaders analysis with brand competition rankings
- Performance Analytics tracking range and technology evolution
- Statistical distributions, market share breakdowns, and correlation heatmaps

## Technologies Used

- **Streamlit** - Web application framework
- **Altair** - Statistical visualization library
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing

## Project Structure
![img.png](images/proj_structure.png)

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/sanctusgee/csca5702-dataviz-final.git
   cd csca5702-dataviz-final
```
2. **Install dependencies**
```bash
   pip install -r requirements.txt
``` 

3. **Run the application**

```bash
streamlit run app.py
```
4. **Open your browser** to http://localhost:8501

### Usage

**Navigation**
Use the sidebar dropdown to navigate between different analysis pages:

- **Home**: Overview and key metrics
- **Executive Dashboard**: Comprehensive KPIs with interactive cross-filtering
- **Price Analytics**: Cost trends and efficiency analysis
- **Geographic Insights**: Location-based adoption patterns
- **Market Leaders**: Brand competition and rankings

**Interactive Features**

- Click on chart elements to filter all related visualizations
- Use sidebar filters to narrow down data by year, price, make, type, or county
- Brush-select areas in scatter plots for detailed segment analysis
- Reset buttons available to clear all selections

**Sample Mode**
For optimal performance, the platform uses intelligent sampling (5,000 data points) while preserving analytical accuracy. Toggle this in the sidebar display options.

---
### Project Highlights

**Data Source**
WA State Open Data Portal
This project uses the official [Washington State Electric Vehicle Population Data ](https://data.wa.gov/Transportation/Electric-Vehicle-Population-Data/f6w7-q2d2/about_data)from the Department of Licensing:
- Contains: 150,000+ records of Battery Electric Vehicles (BEVs) and Plug-in Hybrid Electric Vehicles (PHEVs)
- Attributes: Make, model, electric range, pricing, geographic distribution, registration dates


**Course Information**

CSCA 5702 - Fundamentals of Data Visualization
University of Colorado Boulder

**License**

This project is licensed under the MIT License - see the LICENSE file for details.

**Contributing**

This is an academic project, but feedback and suggestions are welcome! Please feel free to open an issue or submit a pull request.
