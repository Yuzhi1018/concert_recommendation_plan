import joblib
from pathlib import Path


BASE=Path(__file__).resolve().parent
OUT= BASE / "artifacts"

KMeans_model = joblib.load(OUT / "kmeans_model.joblib")
Logistic_model = joblib.load(OUT / "logistic_model.joblib")

