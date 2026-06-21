"""Pure morphology experiment: no lat/lon. Tests whether building shape alone can predict era."""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, classification_report
import xgboost as xgb

DATA = Path(r"D:\PROJELER\ml_data")
ERA_NAMES = ["Tas_Barok","Grunderzeit","Art_Deco","Brutalizm","Prefab","Cam_Celik","Modern"]

GEOM_ONLY = [
    "area_m2","perimeter_m","compactness","aspect_ratio","n_vertices",
    "height","ghsl_neighborhood_year","neighbor_mean_height","building_density_200m",
]

train = pd.read_parquet(DATA / "train.parquet")
test_gt = pd.read_parquet(DATA / "test_gt.parquet")

X_train = train[GEOM_ONLY]
y_train = train["era"].astype(int)
X_test = test_gt[GEOM_ONLY]
y_test = test_gt["era"].astype(int)

pipe = Pipeline([
    ("imp", SimpleImputer(strategy="median")),
    ("sc", StandardScaler()),
    ("m", xgb.XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1,
    )),
])

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="f1_macro", n_jobs=-1)
print(f"Pure geometry CV F1: {cv_scores.mean():.3f} +/- {cv_scores.std():.3f}")

pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)
test_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
print(f"Pure geometry cross-city F1: {test_f1:.3f}")

labels = sorted(set(y_test.tolist() + y_pred.tolist()))
print(classification_report(
    y_test, y_pred,
    labels=labels,
    target_names=[ERA_NAMES[i] for i in labels],
    zero_division=0,
))

imp = sorted(zip(GEOM_ONLY, pipe["m"].feature_importances_), key=lambda x: -x[1])
print("Feature importances:")
for feat, val in imp:
    print(f"  {feat:35s} {val:.4f}")

# Per-city breakdown
print("\nPer-city F1:")
for city in test_gt["city"].unique():
    cdf = test_gt[test_gt["city"] == city]
    if len(cdf) < 5:
        continue
    xc = cdf[GEOM_ONLY]
    yc = cdf["era"].astype(int)
    yp = pipe.predict(xc)
    f = f1_score(yc, yp, average="macro", zero_division=0)
    print(f"  {city:12s}: {len(cdf):5d} | F1={f:.3f}")
