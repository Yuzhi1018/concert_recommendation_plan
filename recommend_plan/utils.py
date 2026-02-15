import json
import os

default_weights={
    'time_score'  : 1,
    'travel_score'  : 2,
    'money_score' : 2,
    'security_score': 1,
    'affection_score' : 3,
    'rarity_score' : 1,
}

templates={
    "money_score": "This session fits your budget well",
    "time_score": "The timing works well for you",
    "travel_score": "Travel time is relatively short",
    "security_score": "The city feels relatively safe",
    "affection_score": "You really like this artist",
    "rarity_score": "This is a relatively rare opportunity",
}

def time_score(event, time_budget_hours: float):
    total = (event.get('travel_hours') or 0) + (event.get('event_duration_hours') or 0)

    if time_budget_hours<=0:
        return 0
    
    if total<= time_budget_hours:
        return 1
    
    over = total-time_budget_hours
    return max(0, 1 - over / time_budget_hours)

def compute_components(event, budget, time_budget_hours):
    if isinstance(event, list):
        event =event[0]

    price = event.get('money')

    if price is None:
        money_score = 0.5
    elif budget >= price:
        money_score = 1.0
    else:
        money_score = max(0.0, 1.0 - (price - budget) / budget)

    rarity_score = event.get('rarity_score', 0.5)

    scores={
        'time_score': time_score(event, time_budget_hours),

        'travel_score': max(0, 1 - event['travel_hours'] / 10),

        'money_score': money_score,

        'security_score': event['security'] / 10,

        'affection_score' : event['level_of_affection_towards_artists'] / 10,

        'rarity_score' : 1 / (1 + event['frequency_of_holding_concerts']),
    }

    return scores

def compute_score(event, budget=400, weights=None, time_budget_hours= 8.0):
    if weights is None:
        weights = default_weights
    
    scores= compute_components(event, budget=budget, time_budget_hours=time_budget_hours)

    total_score = sum(weights[k]*scores[k] for k in scores)

    return total_score

def explain_event(event, budget=400, weights=None, top_n=2, time_budget_hours=8.0):
    if weights is None:
        weights = default_weights
    
    scores = compute_components(event, budget=budget, time_budget_hours=time_budget_hours)
    contributions = {k: weights.get(k,0) * scores[k] for k in scores}

    top_factors = sorted(contributions.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [templates.get(k,k) for k, _ in top_factors]
    
    if event.get('rarity_score', 0) >= 0.75:
        n = event.get('city_event_count', None)
    if n:
        reasons.append(f"Rarity: Only {n} show(s) in {event['city']} for this tour.")
    else:
        reasons.append("Rarity: Limited shows in this city.")    

def rank_events(events, budget=400, time_budget_hours= 8.0, weights=None, k=2):
    if weights is None:
        weights = default_weights

    if isinstance(events, dict):
        events = [events]

    scored = [(e, compute_score(e, budget=budget, time_budget_hours=time_budget_hours, weights=weights)) for e in events]
    scored.sort(key=lambda x: x[1], reverse=True)

    result = []
    for e, total in scored[:k]:
        result.append({
            "event": e,
            "score": total,
            "reasons": explain_event(e, budget=budget, weights=weights, top_n=2),
        })
    return result

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECURITY_PATH = os.path.join(BASE_DIR, "data", "security_json.json")

with open(SECURITY_PATH) as f:
    SECURITY_DATA = json.load(f)


def security_score(event):
    city = event.get('city')
    county = CITY_TO_COUNTY.get(city)

    if not county:
        return 0.5
    
    return SECURITY_DATA.get(county, 0.5)

