import os
from flask import Flask, render_template

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates'))
app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/average_stats')
def average_stats():
    return render_template('average_stats_by_vehicle_type.html')

@app.route('/range_trends')
def range_trends():
    return render_template('electric_range_trends.html')

@app.route('/top_manufacturers')
def top_manufacturers():
    return render_template('top_manufacturers.html')

if __name__ == '__main__':
    app.run(debug=True)
