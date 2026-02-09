default_weights={
    'time_score'  : 0.10,
    'travel_score'  : 0.20,
    'money_score' : 0.20,
    'security_score': 0.10,
    'affection_score' : 0.30,
    'rarity_score' : 0.10,
}

templates={
    "money_score": "This session fits your budget well",
    "time_score": "The timing works well for you",
    "travel_score": "Travel time is relatively short",
    "security_score": "The city feels relatively safe",
    "affection_score": "You really like this artist",
    "rarity_score": "This is a relatively rare opportunity",
}


def compute_score(event, budget=400):
    if isinstance(event, list):
        event =event[0]

    if (budget >= event['money']):
        money_score = 1
    else:
        money_score = max(0, 1 - (event['money'] - budget) / budget)

    scores={
        'time_score': event['time'] / 10,

        'travel_score': max(0, 1 - event['travel_hours'] / 10),

        'money_score': money_score,

        'security_score': event['security'] / 10,

        'affection_score' : event['level_of_affection_towards_artists'] / 10,

        'rarity_score' : 1 / (1 + event['frequency_of_holding_concerts']),
    }

    total_score = sum(default_weights[k]*scores[k] for k in scores)

    return total_score, scores

def explain_event(event, budget=400, weights=None, top_n=2):
    if weights is None:
        weights = default_weights
    
    total, scores = compute_score(event, budget=budget)
    contributions = {k: weights.get(k,0) * scores[k] for k in scores}

    top_factors = sorted(contributions.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [templates.get(k,k) for k, _ in top_factors]

def rank_events(events, budget=400, weights=None, k=2):
    if weights is None:
        weights = default_weights

    if isinstance(events, dict):
        events = [events]

    scored = []
    for e in events:
        total, _ = compute_score(e, budget=budget)
        scored.append((e, total))

    scored.sort(key=lambda x: x[1], reverse=True)

    result = []
    for e, total in scored[:k]:
        result.append({
            "event": e,
            "score": total,
            "reasons": explain_event(e, budget, weights, top_n=2)
        })
    return result
