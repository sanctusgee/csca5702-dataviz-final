# EV Population Visualizations

# EV Population Visualizations (Washington State)

This project visualizes electric vehicle registration data for Washington State, focusing on:

- Average electric range by vehicle type  
- Range trends over time by vehicle type  
- Top manufacturers by vehicle count  

---

## Project Structure

- **data/** — Contains `electric_vehicle_population.csv`
- **src/** — Python code:
  - `ev_advanced_visualizations.py` — Generates Altair visualizations
  - `flask_app.py` — Flask app for deployment
- **templates/** — HTML templates served by Flask
- **docs/** — Static HTML files for GitHub Pages

---

## Deployment

### Local Development

```bash
pip install -r requirements.txt
python src/ev_advanced_visualizations.py
python src/flask_app.py
```

### GitHub Pages
- Push files in docs/ to main branch

- Enable GitHub Pages in repo settings

### Heroku
Deploy with:

```git push heroku main```

Visit: https://your-ev-visualizations.herokuapp.com

### Reports
See report.md for evaluation and design details.

### License
MIT

