import requests
import json
import os
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render,redirect
from .utils import rank_events, compute_score, explain_event
from django.http import JsonResponse
from .importers import fetch_tm_events_by_keyword, tm_to_internal_event
from .maps import get_travel_hours_mapbox
from collections import Counter
from .segmentation import predict_cluster, cluster_profile
from .OpenAI_api_connection import generate_ai_plan
from .models import SearchHistory

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #绝对路径
DATA_PATH = os.path.join(BASE_DIR, "data", 'events.json')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
        
    return render(request, 'recommend_plan/signup.html', {'form': form})
    

def index(request):
#set default value for variables users should input
    top_city = None
    result =[]
    artist = ''
    budget = 400
    time_budget_hours= 8.0
    no_recent_tour =False
    user_city=""
    affection=7

    if request.method =="POST":
        
        artist= (request.POST.get('artist') or'').strip()

        budget_raw = (request.POST.get("budget") or "").strip()

        budget = int(budget_raw) if budget_raw.isdigit() else 400

        time_raw = (request.POST.get('time_budget_hours') or "").strip()

        user_city= (request.POST.get('user_city') or '').strip()

        affection_raw = (request.POST.get('affection') or '7').strip()
        
        affection = int(affection_raw) if affection_raw.isdigit() else 7

        affection = max(1, min(10,affection))

        weights={
            'money_score': float(request.POST.get('pref_cost', 2)),
            'time_score': float(request.POST.get('pref_time', 1)),
            'travel_score': float(request.POST.get('pref_travel', 2)),
            'security_score': float(request.POST.get('pref_security', 1)),
            'affection_score': float(request.POST.get('pref_affection', 3)),
            'rarity_score': float(request.POST.get('pref_rarity',1)),
        }

        total_weight = sum(weights.values())
        if total_weight>0:
            weights = {k: v / total_weight for k, v in weights.items()}
        else:
            weights = weights
        try:
            time_budget_hours=float(time_raw) if time_raw else 8.0
        except ValueError:
            time_budget_hours = 8.0

        tm_events = fetch_tm_events_by_keyword(artist)

        events = [tm_to_internal_event(e, user_city) for e in tm_events]

        for e in events:
            e['level_of_affection_towards_artists'] = affection

        city_counts = Counter(e.get('city') for e in events if e.get('city'))

        for e in events:
            n = city_counts.get(e.get('city'),1)
            e['rarity_score'] = max(0.0, 1.0- (n-1)/4.0)
            e['city_event_count'] = n

        from .maps import get_travel_hours_mapbox

        for e in events:
            try:
                e['travel_hours'] = get_travel_hours_mapbox(user_city, e.get('city'))
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
            top_event = result[0]['event']
            reasons = result[0]['reasons']

            request.session['top_event'] = top_event
            request.session['reasons'] = reasons
            request.session['artist'] = artist
        
        if not result:
            no_recent_tour = True

        if request.user.is_authenticated and top_city:
            SearchHistory.objects.create(
                user=request.user,
                artist=artist,
                budget=budget,
                top_city=top_city,
            )

    return render(request, "recommend_plan/index.html", {
        "top_city": top_city,
        "result": result,
        "artist": artist,
        'budget': budget,
        'time_budget_hours': time_budget_hours,
        'no_recent_tour': no_recent_tour,
        'user_city': user_city,
        'affection': affection
    })

def search_concerts(request):
    artist = request.GET.get('artist','')
    API_KEY = os.getenv('TICKETMASTER_API_KEY')

    url = "https://app.ticketmaster.com/discovery/v2/events.json?apikey=K2M2PpHCgz61NMAUmV2ppgZ5pkgAJ7ra&keyword=taylor%20swift&size=3"
    params = {
        'apikey': API_KEY,
        'keyword': artist,
        'size': 5
    }

    r = requests.get(url, params=params)
    data = r.json()
    
    return JsonResponse(data)

def get_user_segment(form_data):
    cluster_id = predict_cluster(form_data)
    profile = cluster_profile(cluster_id)
    return cluster_id, profile

def cluster_profile(cluster_id):
    profiles = {
        0: {
            'name': 'Budget-first Explorer',
            'prompt_hint': 'Focus on affordability, transportation savings, and value-for-money tradeoffs.',
        },
        1: {
            'name':'Safety-conscious Planner',
            'prompt_hint': 'Focus on safety, lower-risk travel planning, comfortable logistics, and practical scheduling.',
        },
        2:{
            'name':'Artist-driven Fan',
            'prompt_hint': 'Focus on emotional value, rarity of the event, artist appeal, and why the experience may be worth the effort.',
        }
    }
    return profiles.get(cluster_id, {
        'name':'Balanced User',
        'prompt_hint':'Give a balanced recommendation considering cost, convenience, and experience.'
    })
def weights_view(request):
    factors = [
        ("Travel distance & difficulty", "pref_travel"),
        ("Cost consideration", "pref_cost"),
        ("Time constraints & pressure", "pref_time"),
        ("Environmental conditions", "pref_environment"),
        ("Urban safety", "pref_safety"),
        ("Artist-related considerations", "pref_artist"),
        ("Affection towards artist", "pref_affection"),
    ]

    if request.method == "POST":
        request.session['weights'] = {
            'travel' : float(request.POST.get('pref_travel')),
            'time' : float(request.POST.get('pref_time')),
            'money': float(request.POST.get('pref_cost')),
            'safety': float(request.POST.get('pref_safety')),
            'environmental_condition': float(request.POST.get('pref_environment')),
            'artist-related': float(request.POST.get('pref_artist')),
            'affection_towards_artist': float(request.POST.get('pref_affection'))
        }
        return redirect('recommend_plan:index')
    return render(request, 'weights.html', {
        'factors': factors
    })

def openai_page(request):
    plan = None

    if request.method == "POST":
        city = request.POST.get('city')
        venue = request.POST.get('venue')
        date = request.POST.get('date')
        reasons = request.POST.getlist('reasons')
        artist = request.session.get('artist')

        payload = {
            "user": {
                "artist": artist,
            },
            "event": {
                "city": city,
                "venue": venue,
                'date': date,
            },
            'reasons': reasons,
        }

        plan = generate_ai_plan(payload)
    
    return render(request, 'recommend_plan/openai.html', {
        'plan':plan,
        'artist': artist,
        'city': city,
        'venue': venue,
        'date': date,})