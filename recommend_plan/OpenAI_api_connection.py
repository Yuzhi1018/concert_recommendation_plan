from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_plan(payload):
    event = payload.get('event', {})
    reasons = payload.get('reasons')

    prompt = f"""
    You are a smart concert travel planner.

    Event info:
    {event}

    Reasons why user likes it:
    {reasons}

    Generate a personalized travel plan for this concert, including:
    - Why this concert is worth attending
    - Travel suggestion
    - Budget tips
    - Experience highlights
    """
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "system", "content": "You are a helpful planner."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7,
    )

    return response.choices[0].message.content