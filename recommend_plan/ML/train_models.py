import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
from pathlib import Path
import joblib

class KMeansClusterer(BaseEstimator, TransformerMixin):
    def __init__(self, n_clusters=3, random_state=42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.pipe_ = None

    def fit(self, X, y=None):
        self.pipe_ = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ("scaler", StandardScaler()),
            ("kmeans", KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init='auto'))
        ])
        self.pipe_.fit(X)
        return self
    
    def transform(self, X):
        clusters = self.pipe_.predict(X).reshape(-1, 1)
        return clusters
    
# ===== Load data =====
BASE = Path(__file__).resolve().parent
OUT = './artifacts'
df = pd.read_csv(BASE / "concert_plan_dataset.csv")

features = [
    'Cost Considerations',
    'Travel Distance & Difficulty',
    'Time Constraints & Real-life Pressure',
    'Environmental Conditions',
    'Urban Safety',
    'Artist-related Considerations',
    'Personal Preferences'
]

y=(df['Q12 (coded response)'].astype(float)>=4).astype(int)
x = df[features].copy()

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)

clusterer = KMeansClusterer(n_clusters=3, random_state=42)

numeric_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ("scaler", StandardScaler())
])

cluster_transformer = Pipeline([
    ('onehot', OneHotEncoder(handle_unknown='ignore', drop='first')),
])

preprocess = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, features),
        ('cluster', Pipeline([('km', clusterer), ('ohe', cluster_transformer)]), features),
    ]
)
# ===== Logistic pipeline =====
model = Pipeline([
    ('preprocess', preprocess),
    ('clf', LogisticRegression(
            max_iter=5000,
            class_weight='balanced',
            solver='liblinear',
            C=0.2
            ))
])

model.fit(x_train, y_train)

#take out the result of cluster distribution and cluster center
clusterer = model.named_steps['preprocess']\
                 .transformers_[1][1]\
                 .named_steps['km']

train_clusters = clusterer.transform(x_train)
test_clusters = clusterer.transform(x_test)

print('Train cluster counts:')
print(pd.Series(train_clusters.ravel()).value_counts())

km_model = clusterer.pipe_.named_steps['kmeans']
scaler = clusterer.pipe_.named_steps['scaler']

centers_scaled = km_model.cluster_centers_
centers = scaler.inverse_transform(centers_scaled)

centers_df = pd.DataFrame(centers, columns=features)
pd.set_option('display.max_columns', None)
print(centers_df.round(2))

y_prob = model.predict_proba(x_test)[:, 1]
y_pred = (y_prob >= 0.5).astype(int)

print('\nAccuracy:', accuracy_score(y_test, y_pred))
print('ROC-AUC:', roc_auc_score(y_test, y_prob))
print('\nClassification Report:\n', classification_report(y_test, y_pred))

joblib.dump(model, OUT / 'kmeans_pipe.joblib')
centers_df.to_csv(OUT / 'cluster_centers.csv', index=False)