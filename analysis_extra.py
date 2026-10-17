"""Extra measurements for the report: threshold sensitivity + latency."""
import json, time, statistics
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from fraud_detector.model import FraudModel, generate_synthetic
from fraud_detector.engine import Transaction, evaluate
from fraud_detector.api import create_app

m = FraudModel()
X, y = generate_synthetic(seed=42)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
proba = m.predict_proba(Xte)
rows = []
for th in (0.10, 0.20, 0.30, 0.40, 0.50, 0.75):
    p = (proba >= th).astype(int)
    rows.append(dict(threshold=th, accuracy=round(accuracy_score(yte, p), 4),
                     precision=round(precision_score(yte, p, zero_division=0), 4),
                     recall=round(recall_score(yte, p), 4), f1=round(f1_score(yte, p), 4)))
print(json.dumps(rows, indent=1))

t = Transaction(85000, 2, 2, True, True, 200)
N = 2000
lat = []
for _ in range(N):
    s = time.perf_counter(); evaluate(t, m.score); lat.append((time.perf_counter() - s) * 1000)
eng = dict(n=N, mean_ms=round(statistics.mean(lat), 3), p95_ms=round(float(np.percentile(lat, 95)), 3))
app = create_app(m); app.config["TESTING"] = True; c = app.test_client()
body = dict(amount=85000, hour=2, txn_last_hour=2, account_age_days=200, is_foreign=True, is_new_device=True)
lat2 = []
for _ in range(500):
    s = time.perf_counter(); c.post("/api/assess", json=body); lat2.append((time.perf_counter() - s) * 1000)
api = dict(n=500, mean_ms=round(statistics.mean(lat2), 3), p95_ms=round(float(np.percentile(lat2, 95)), 3))
print("engine+model latency", eng); print("API latency (Flask test client)", api)
json.dump(dict(thresholds=rows, engine_latency=eng, api_latency=api, test_set=int(len(yte)),
               test_frauds=int(yte.sum())), open("results/extra.json", "w"), indent=1)
