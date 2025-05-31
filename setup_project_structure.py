import os

# Define directories
dirs = [
    'data',
    'src',
    'templates',
    'docs'
]

# Define files and placeholder content
files = {
    '.gitignore': '__pycache__/\n*.pyc\n.env\n',
    'README.md': '# EV Population Visualizations\n\nSee `report.md` for details.',
    'report.md': '# Project Report\n\nThis report will detail project design, evaluation, and insights.',
    'requirements.txt': 'pandas\naltair\nflask\ngunicorn\n',
    'Procfile': 'web: gunicorn src.flask_app:app\n',
    'LICENSE': 'MIT License\n',
    'templates/index.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EV Population Visualizations</title>
</head>
<body>
    <h1>EV Population Visualizations (Washington State)</h1>
    <ul>
        <li><a href="/average_stats">Average Stats by Vehicle Type</a></li>
        <li><a href="/range_trends">Electric Range Trends</a></li>
        <li><a href="/top_manufacturers">Top Manufacturers by Count</a></li>
    </ul>
</body>
</html>
''',
    'docs/index.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EV Population Visualizations</title>
</head>
<body>
    <h1>EV Population Visualizations (Washington State)</h1>
    <ul>
        <li><a href="average_stats_by_vehicle_type.html">Average Stats by Vehicle Type</a></li>
        <li><a href="electric_range_trends.html">Electric Range Trends</a></li>
        <li><a href="top_manufacturers.html">Top Manufacturers by Count</a></li>
    </ul>
</body>
</html>
'''
}

# Create directories
for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"Created: {d}")

# Create files
for path, content in files.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created: {path}")

# Create src placeholders
for script in ['ev_advanced_visualizations.py', 'flask_app.py']:
    with open(f'src/{script}', 'w', encoding='utf-8') as f:
        f.write('# Placeholder script\n')
    print(f"Created: src/{script}")

print("Project structure set up successfully!")
