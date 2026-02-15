import os
import requests
import math
from datetime import date, datetime
from .maps import get_travel_hours_mapbox

TM_EVENTS_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

def fetch_attraction_id(artist: str, TICKETMASTER_API_KEY):
    url = "https://app.ticketmaster.com/discovery/v2/attractions.json"
    params = {
        "keyword": artist,
        'apikey': TICKETMASTER_API_KEY
    }
    r= requests.get(url, params=params)
    data= r.json()

    attractions= data.get('_embedded', {}).get('attractions', [])
    if not attractions:
        return None
    
    return attractions[0]['id']


def fetch_tm_events_by_keyword(keyword: str, country_code: str = "US", size: int = 10):
    """
    Calls Ticketmaster Discovery API v2 events search.
    Requires apikey query parameter.
    """
    api_key = os.environ.get("TICKETMASTER_API_KEY")
    if not api_key:
        raise RuntimeError("Missing env var: TICKETMASTER_API_KEY")

    params = {
        "apikey": api_key,          # required :contentReference[oaicite:2]{index=2}
        "keyword": keyword,         # example usage :contentReference[oaicite:3]{index=3}
        "countryCode": country_code,
        "classificationName": "music",
        "size": size,
        "sort": "date,asc",
    }

    r = requests.get(TM_EVENTS_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data.get("_embedded", {}).get("events", [])

def extract_price_min_max_currency(tm_event: dict):
    """"
    从 Ticketmaster event中提取价格区间:
    返回 (min_price, max_price, currency), 都可能为None
    """
    prs = tm_event.get('priceRanges')
    if not prs or not isinstance(prs, list):
        return None, None, None
    
    mins = []
    maxs = []
    currency = None
    
    for pr in prs:
        if not isinstance(pr, dict):
            continue
        mn = pr.get('min')
        mx = pr.get('max')
        cur = pr.get('currency')

        if isinstance(mn, (int, float)):
            mins. append(float(mn))
        if isinstance(mx, (int, float)):
            maxs.append(float(mx))
        if currency is None and isinstance(cur, str):
            currency=cur
        
    if not mins and not maxs:
        return None, None, currency
    
    min_price = min(mins) if mins else None
    max_price = max(maxs) if maxs else None
    return min_price, max_price, currency

def tm_to_internal_event(tm_event: dict, user_city) -> dict:
    """
    Map Ticketmaster event -> your internal scoring schema.
    Fill missing fields with defaults for now.
    """
    venues = tm_event.get("_embedded", {}).get("venues", [])
    venue = venues[0] if venues else {}

    county = city_to_county_map.get(city)
    venue_name = venue.get("name", "Unknown Venue")
    date = (tm_event.get("dates", {}).get("start") or {}).get("localDate")  # YYYY-MM-DD

    images = tm_event.get("images", []) or []
    poster_url = images[0].get("url") if images else None
    price_min, price_max, currency =extract_price_min_max_currency(tm_event)
    travel_hours = get_travel_hours_mapbox(user_city, city)

    # Defaults (later replace with questionnaire/user input)
    return {
        "city": city,
        "time": 7,
        "money": price_min,
        "travel_hours": travel_hours,
        "security": 6,
        "level_of_affection_towards_artists": 7,
        "frequency_of_holding_concerts": 2,

        # extra fields for display
        "date": date,
        "venue": venue_name,
        "ticketmaster_url": tm_event.get("url"),
        "poster_url": poster_url,
        "event_name": tm_event.get("name"),
    }
