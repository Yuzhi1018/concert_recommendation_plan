import json
import os
from django.shortcuts import render
from .utils import rank_events, compute_score, explain_event

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", 'events.json')

def index(request):
    recommendation = None
    reasons = []

    if request.method =="POST":
        artist= request.POST.get('artist','').strip()
        budget = int(request.POST.get('budget', 400))

        tm_events = fetch_ticketmaster_events(artist)

        events = [tm_to_internal_event(e) for e in tm_events]

        scored = [(e, compute_score(e, budget)) for e in events]
        scored.sort(key=lambda x:x[1], reverse=True)

        if scored:
            top_event = scored[0][0]
            recommendation = top_event['city']
            reasons = explain_event(top_event, budget)

    return render(request, "recommend_plan/index.html", {
        'recommendation': recommendation,
        'reasons': reasons
    })

