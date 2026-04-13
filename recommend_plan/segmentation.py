
from pathlib import Path
import pandas as pd
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = BASE_DIR / 'artifacts'
KMEANS_PATH = ARTIFACTS_DIR / 'kmeans_pipe.joblib'
CENTERS_PATH = ARTIFACTS_DIR / 'cluster_centers.csv'

FEATURES = [
    'Cost Considerations',
    'Travel Distance & Difficulty',
    'Time Constraints & Real-life Pressure',
    'Environmental Conditions',
    'Urban Safety',
    'Artist-related Considerations',
    "Personal Preferences",
]

_kmeans_pipe = None
_centers_df = None

def get_kmeans_pipe():
    global _kmeans_pipe
    if _kmeans_pipe is None:
        _kmeans_pipe = joblib.load(KMEANS_PATH)
    return _kmeans_pipe

def get_centers_df():
    global _centers_df
    if _centers_df is None:
        _centers_df = pd.read_csv(CENTERS_PATH)
    return _centers_df

def predict_cluster(user_inputs: dict) -> int:
    row = {f: float(user_inputs.get(f, 0)) for f in FEATURES}
    X = pd.DataFrame([row], columns=FEATURES)

    pipe = get_kmeans_pipe()
    cluster_id = int(pipe.predict(X)[0])
    return cluster_id

def cluster_profile(cluster_id: int) -> dict:
    centers = get_centers_df()
    s = centers.iloc[cluster_id]
    return {k: float(s[k]) for k in FEATURES }