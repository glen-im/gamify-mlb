from flask import Flask, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Cache the data in memory
mlb_hr_csvs_list = [
    'https://storage.googleapis.com/gcp-mlb-hackathon-2025/datasets/2016-mlb-homeruns.csv',
    'https://storage.googleapis.com/gcp-mlb-hackathon-2025/datasets/2017-mlb-homeruns.csv',
    'https://storage.googleapis.com/gcp-mlb-hackathon-2025/datasets/2024-mlb-homeruns.csv',
    'https://storage.googleapis.com/gcp-mlb-hackathon-2025/datasets/2024-postseason-mlb-homeruns.csv'
]

def load_data():
    mlb_hrs = pd.DataFrame({'csv_file': mlb_hr_csvs_list})
    mlb_hrs['season'] = mlb_hrs['csv_file'].str.extract(r'/datasets/(\d{4})')
    mlb_hrs['hr_data'] = mlb_hrs['csv_file'].apply(pd.read_csv)

    for index, row in mlb_hrs.iterrows():
        hr_df = row['hr_data']
        hr_df['season'] = row['season']

    all_mlb_hrs = pd.concat(mlb_hrs['hr_data'].tolist(), ignore_index=True)[
        ['season', 'play_id', 'title', 'ExitVelocity', 'LaunchAngle', 'HitDistance', 'video']
    ]
    
    # Convert numeric columns to float and handle NaN values
    numeric_columns = ['ExitVelocity', 'LaunchAngle', 'HitDistance']
    for col in numeric_columns:
        all_mlb_hrs[col] = pd.to_numeric(all_mlb_hrs[col], errors='coerce')
        # Replace NaN with 0
        all_mlb_hrs[col] = all_mlb_hrs[col].fillna(0)
    
    return all_mlb_hrs

# Route to serve the main HTML page
@app.route('/')
def home():
    return send_file('index.html')

# API endpoint to get MLB data
@app.route('/api/mlb-data')
def get_mlb_data():
    try:
        # Load data (in production, you'd want to cache this)
        df = load_data()
        
        # Replace any remaining NaN or infinite values with 0 before converting to dict
        df = df.replace([np.inf, -np.inf, np.nan], 0)
        
        # Convert to dictionary format with explicit float conversion for numbers
        data = df.to_dict('records')
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)