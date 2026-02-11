import requests
import json
import os
from django.shortcuts import render
from .utils import rank_events, compute_score, explain_event
from django.http import JsonResponse
from .importers import fetch_tm_events_by_keyword, tm_to_internal_event

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", 'events.json')

def index(request):
    top_city = None
    result =[]
    artist = ''
    budget = 400
    time_budget_hours= 8.0
    no_recent_tour =False
    user_city=""

    if request.method =="POST":
        
        artist= (request.POST.get('artist') or'').strip()

        budget_raw = (request.POST.get("budget") or "").strip()

        budget = int(budget_raw) if budget_raw.isdigit() else 400

        time_raw = (request.POST.get('time_budget_hours') or "").strip()

        user_city= (request.POST.get('user_city') or '').strip()

        try:
            time_budget_hours=float(time_raw) if time_raw else 8.0
        except ValueError:
            time_budget_hours = 8.0

        tm_events = fetch_tm_events_by_keyword(artist)

        events = [tm_to_internal_event(e) for e in tm_events]

        from .maps import get_travel_hours_cached

        for e in events:
            try:
                e['travel_hours'] = get_travel_hours_cached(user_city, e.get('city'))
            except Exception:
                e['travel_hours'] = 8.0

        result = rank_events(
            events,
            budget=budget,
            time_budget_hours=time_budget_hours,
            k=2
        )
        
        if result:
            top_city = result[0]['event']['city']
        if not result:
            no_recent_tour = True
    return render(request, "recommend_plan/index.html", {
        "top_city": top_city,
        "result": result,
        "artist": artist,
        'budget': budget,
        'time_budget_hours': time_budget_hours,
        'no_recent_tour': no_recent_tour,
        'user_city': user_city
    })

def search_concerts(request):
    artist = request.GET.get('artist','')
    API_KEY = os.getenv('K2M2PpHCgz61NMAUmV2ppgZ5pkgAJ7ra')

    url = "https://app.ticketmaster.com/discovery/v2/events.json?apikey=K2M2PpHCgz61NMAUmV2ppgZ5pkgAJ7ra&keyword=taylor%20swift&size=3"
    params = {
        'apikey': API_KEY,
        'keyword': artist,
        'size': 5
    }

    r = requests.get(url, params=params)
    data = r.json()
    
    return JsonResponse(data)

