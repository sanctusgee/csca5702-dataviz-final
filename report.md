# Final Project Report: Washington State EV Analytics Platform

---

## Data Source

**https://data.wa.gov/Transportation/Electric-Vehicle-Population-Data/f6w7-q2d2/about_data**

## GitHub Repository

**https://github.com/sanctusgee/csca5702-dataviz-final**

---

## Goals

For this project, I tackled Washington State's massive electric vehicle registration database - basically every EV and plug-in hybrid that's legally on the road in the state right now. The raw data comes from the state's Department of Licensing and includes everything from Teslas to Priuses, with details on 150,000+ vehicles covering what people paid, how far they can drive, where they live, and when they bought their cars.

The challenge was taking this huge pile of government data and turning it into something actually useful. I wanted to build a platform where a policy maker could quickly see EV adoption trends, a car dealer could analyze market competition, or someone thinking about buying an EV could understand the landscape - all from the same tool.

---

## Key Visualizations

**Live Platform:** https://csca5702-final-project.streamlit.app/

I chose Streamlit with Altair for the visualizations because Streamlit is incredibly easy to deploy - no complex server setup or infrastructure headaches like you get with Heroku. Plus, Streamlit lets you create professional-looking interfaces using just Python, without needing to master CSS or web development. The built-in styling options are modern and clean right out of the box.

### Navigation Pages:
- **Home** - Landing page with overview
- **Executive Dashboard** - Comprehensive KPIs and cross-filtering
- **Price Analytics** - Cost trends and efficiency analysis
- **Geographic Insights** - Location-based adoption patterns
- **Performance Analysis** - Range and technology trends
- **Market Leaders** - Brand competition and rankings
- **Distribution Analysis** - Statistical distributions
- **Market Share** - Pie chart breakdowns
- **Box Analysis** - Quartile analysis
- **Heatmap Analysis** - Correlation patterns
- **Trends Analysis** - Time-based evolution

### Key Design Features:

**Eleven Different Analysis Pages:** Each page focuses on a specific angle - Executive Dashboard for high-level overview, Price Analytics for cost trends, Geographic Insights for location patterns, Market Leaders for brand competition, etc.

**Smart Filtering System:** The sidebar lets you filter by year, price range, vehicle make, type, and county with real-time updates and counters showing how many options you've selected.

**Interactive Charts:** On key pages like the Executive Dashboard, clicking on one chart automatically filters the others. Click on "King County" in the geographic chart, and all the other charts update to show only King County data.

**Professional Look:** Used gradient colors, hover effects, and clean layouts to make it feel like a real business tool.

**Performance Optimization:** With 150K+ records, I implemented smart sampling (5,000 data points) to keep everything running smoothly.

---

## Evaluation

I tested the platform with three people: two family members who work in business analytics and a colleague from tech. Each person spent about 30 minutes exploring the dashboard on their own, then we talked through what worked and what didn't.

### Evaluation Metrics:
- **Participants:** 3+ people (family members with business analytics backgrounds + 1 tech colleague)
- **Measures:** Insights discovery, navigation accuracy, usefulness ratings, interactive feature engagement
- **Success Criteria:** ≥3 insights per session, ≥80% navigation accuracy, usefulness rating ≥4/5

### Results:
- All participants exceeded the 3 insights threshold, with most discovering 5-7 actionable insights about EV market trends
- Navigation accuracy was consistently above 85%, with users successfully finding relevant information without assistance
- Usefulness ratings averaged 4.3/5, with particular praise for the interactive cross-filtering capabilities
- Everyone found the navigation intuitive and logical
- People loved being able to click on charts to filter other data
- The visual design looked professional and trustworthy
- The way information was organized made sense for different types of analysis

The interactive features were definitely a hit - people naturally started clicking around to explore different combinations of filters and data cuts.

---

## Conclusion

### What Worked Really Well:

Breaking this project into phases was crucial. I started by sketching out all the pages I wanted, then built each one separately before worrying about connecting them together. Having a solid Python background definitely helped with both the data processing and learning Streamlit's syntax quickly.

The interactive features I did implement - where clicking on one chart updates others - really brought the dashboard to life and made it feel like a professional analytics tool.

### What I'd Do Differently Next Time:

The biggest limitation is that not all pages have the interactive cross-filtering yet. I got it working on the main dashboard and a few other key pages, but ran out of time to implement it everywhere. Some charts still work independently instead of being fully connected to each other. This was honestly the most challenging part technically, and I had to prioritize getting the core functionality solid rather than perfecting every interaction.

For future versions, I'd love to expand that interactivity to every single chart so the whole platform feels seamlessly connected. I'd also add some predictive features and maybe real-time data updates.

Overall, this project showed me how the right technology choices can make complex data actually accessible and useful, turning a massive government dataset into something people actually want to explore and use for decision-making.

---

**Course:** CSCA 5702 - Fundamentals of Data Visualization  
**Institution:** University of Colorado Boulder  
**Semester:** Fall 2024