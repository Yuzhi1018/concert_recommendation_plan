import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
from pathlib import Path

BASE= Path(__file__).resolve().parent
OUT= BASE / "artifacts"

df = pd.read_csv(BASE / "concert_plan_dataset.csv")
features = ['budget', 'time_budget_hours', 'affection', 'rarity_score', 'city_event_count']
X = df[features]
y = df['attended']
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('kmeans', KMeans(n_clusters=3, random_state=42)),
    ('logreg', LogisticRegression(random_state=42))
])
pipeline.fit(X, y)
OUT.mkdir(exist_ok=True, parents=True)
joblib.dump(pipeline, OUT / "concert_recommendation_model.pkl")
