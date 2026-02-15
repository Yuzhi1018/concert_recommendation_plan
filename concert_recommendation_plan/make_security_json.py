import pandas as pd
import json
from pathlib import Path
df = pd.read_csv('/Users/amanda_tian/Desktop/crime_data_w_population_and_crime_rate.csv')
min_rate = df['crime_rate_per_100000'].min()
max_rate = df['crime_rate_per_100000'].max()
df ['security_score'] = 1 - (df['crime_rate_per_100000']-min_rate)/(max_rate-min_rate)
security_json = df.set_index('county_name')['security_score'].to_dict()

OUT_PATH = Path('/Users/amanda_tian/concert_plan_recommender/recommend_plan/data/security_json.json')
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(OUT_PATH, 'w') as f:
    json.dump(security_json, f, indent=2)
