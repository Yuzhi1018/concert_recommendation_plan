import os,requests
from functools import lru_cache

MAPBOX_TOKEN= os.getenv("MAPBOX_TOKEN")

print("TOKEN:", MAPBOX_TOKEN)

@lru_cache(maxsize=512)
def geocode_city(city: str):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{city}.json"
    params= {'access_token': MAPBOX_TOKEN, 'limit':1}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    if not data.get('features'):
        return None
    lon, lat = data['features'][0]['center']
    return lon, lat

@lru_cache(maxsize=2048)
def get_travel_hours_mapbox(origin_city: str, dest_city: str, profile: str='driving'):
    if not MAPBOX_TOKEN:
        return None

    o = geocode_city(origin_city)
    d = geocode_city(dest_city)
    if not o or not d:
        return None
    
    (olon, olat), (dlon, dlat) = o, d
    url= f"https://api.mapbox.com/directions/v5/mapbox/{profile}/{olon},{olat};{dlon},{dlat}"
    params = {'access_token': MAPBOX_TOKEN, 'overview': 'false'}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status
    data = r.json()

    routes = data.get('routes') or []
    if not routes:
         return None
    
    seconds = routes[0]['duration']
    return seconds/ 3600.0