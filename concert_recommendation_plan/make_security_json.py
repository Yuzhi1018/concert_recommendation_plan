import re
import pandas as pd
import json
from pathlib import Path
df = pd.read_csv('/Users/amanda_tian/Desktop/crime_data_w_population_and_crime_rate.csv')
min_rate = df['crime_rate_per_100000'].min()
max_rate = df['crime_rate_per_100000'].max()
df ['security_score'] = 1 - (df['crime_rate_per_100000']-min_rate)/(max_rate-min_rate)
county_security = df.set_index('county_name')['security_score'].round(3).to_dict()

CITY_TO_COUNTY_PATH = Path('recommend_plan/data/city_to_county.json')

with open(CITY_TO_COUNTY_PATH, "r") as f:
    city_to_county = json.load(f)

city_security = {}

def norm_county(name: str) ->str:
    if not name:
        return ""
    s= name.strip().lower()
    s= s.split(',')[0].strip()
    s = re.sub(r"\bcounty\b", "", s)
    s = re.sub(r"\bparish\b", "", s)
    s = re.sub(r"\bborough\b", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

county_security_norm = {norm_county(k): v for k, v in county_security.items()}
city_security = {}
missing2 = []

for city, county in city_to_county.items():
    key = norm_county(county)
    score = county_security_norm.get(key)
    if score is None:
        missing2.append((city, county))
        score=0.5
    city_security[city] = score

OUT_PATH = Path('/Users/amanda_tian/concert_plan_recommender/recommend_plan/data/security_city.json')
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(OUT_PATH, 'w') as f:
    json.dump(city_security, f, indent=2)

print('security_city.json generated successfully!')
print("Missing after normalize:", len(missing2))
print("First 10 missing after normalize:", missing2[:10])