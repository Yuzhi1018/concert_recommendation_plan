import requests
import os

MAPBOX_TOKEN= os.getenv("MAPBOX_TOKEN")

_CACHE = {}

def get_travel_hours_cached(city_a: str, city_b: str) -> float:
    if not city_a or not city_b:
        return 0.0
    
    key = (city_a.strip().lower(), city_b.strip().lower())
    if key in _CACHE:
        return _CACHE[key]
    
    def geocode(city):
        url= f"https://api.mapbox.com/geocoding/v5/mapbox.places/{city}.json"
        params = {
            "access_token": MAPBOX_TOKEN,
            "limit": 1
        }
        r = requests.get(url, params=params, timeout=10).json()
        if not r.get('features'):
            raise ValueError(f'Cannot geocode city: {city}')
        return r['features'] [0] ['center']
    
    lon1, lat1 = geocode(city_a)
    lon2, lat2 = geocode(city_b)

    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{lon1},{lat1};{lon2},{lat2}"
    params = {"access_token": MAPBOX_TOKEN}
    r = requests.get(url, params=params, timeout=10).json()

    routes = r.get('routes') or []
    if not routes:
        raise ValueError('No route found')
    
    seconds = routes[0]['duration']
    hours = seconds / 3600.0

    _CACHE[key] = hours
    return hours
import os
print("MAPBOX KEY:", os.getenv("MAPBOX_TOKEN"))
