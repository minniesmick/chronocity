"""
ML-2: XGBoost + PyTorch MLP era classifier training.

Usage:
  python train_model.py               # train both, save best
  python train_model.py --model xgb   # XGBoost only
  python train_model.py --model mlp   # MLP only
  python train_model.py --eval        # cross-city evaluation only

Outputs:
  backend/era_model.pkl   — best sklearn pipeline (XGBoost or MLP wrapper)
  backend/era_model_xgb.json
"""

import argparse
import pickle
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import xgboost as xgb

DATA = Path(r"D:\PROJELER\ml_data")
BACKEND = Path(__file__).parent.parent

# neighbor_mean_year / neighbor_std_year excluded: circular feature.
# In test cities <3% labeled → city median fills → noise, not signal.
# Academic finding: cross-city transfer without label propagation is hard.
FEATURE_COLS = [
    "area_m2", "perimeter_m", "compactness", "aspect_ratio", "n_vertices",
    "height", "dist_to_center_km", "ghsl_neighborhood_year",
    "neighbor_mean_height", "building_density_200m", "lat", "lon",
]

ERA_NAMES = ["Tas_Barok", "Grunderzeit", "Art_Deco", "Brutalizm", "Prefab", "Cam_Celik", "Modern"]


def load_data():
    train = pd.read_parquet(DATA / "train.parquet")
    test_gt = pd.read_parquet(DATA / "test_gt.parquet")
    print(f"Train: {len(train)} buildings | Test GT: {len(test_gt)} buildings")
    print(f"Train era dist:\n{train['era'].value_counts().sort_index().rename(lambda i: ERA_NAMES[int(i)])}")
    return train, test_gt


def prep(df):
    X = df[FEATURE_COLS].copy()
    y = df["era"].astype(int)
    return X, y


def train_xgboost(train, test_gt):
    print("\n=== XGBoost Baseline ===")
    X_train, y_train = prep(train)
    X_test, y_test = prep(test_gt)

    pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", xgb.XGBClassifier(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=-1,
        )),
    ])

    # 5-fold CV on train
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="f1_macro", n_jobs=-1)
    print(f"  CV F1-macro: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

    # Fit on all train, eval on test_gt
    pipe.fit(X_train, y_train)

    if len(X_test) > 0:
        y_pred = pipe.predict(X_test)
        test_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
        print(f"  Test GT F1-macro: {test_f1:.3f}")
        print(f"\n  Classification Report (test cities):")
        labels_present = sorted(set(y_test.tolist() + y_pred.tolist()))
        print(classification_report(
            y_test, y_pred,
            labels=labels_present,
            target_names=[ERA_NAMES[i] for i in labels_present],
            zero_division=0,
        ))
        cm = confusion_matrix(y_test, y_pred, labels=labels_present)
        print(f"  Confusion matrix:\n{cm}")
    else:
        test_f1 = 0.0

    # Feature importance
    model = pipe.named_steps["model"]
    importances = model.feature_importances_
    feat_imp = sorted(zip(FEATURE_COLS, importances), key=lambda x: -x[1])
    print("\n  Feature importances (top 10):")
    for feat, imp in feat_imp[:10]:
        print(f"    {feat:30s} {imp:.4f}")

    # Save XGBoost model
    model.save_model(str(BACKEND / "era_model_xgb.json"))
    print(f"\n  Saved: era_model_xgb.json")

    return pipe, cv_scores.mean(), test_f1


def train_mlp(train, test_gt):
    print("\n=== PyTorch MLP ===")
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import TensorDataset, DataLoader
    except ImportError:
        print("  torch not installed, skipping MLP")
        return None, 0.0, 0.0

    X_train_raw, y_train = prep(train)
    X_test_raw, y_test = prep(test_gt)

    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()

    X_train_np = scaler.fit_transform(imputer.fit_transform(X_train_raw))
    X_test_np = scaler.transform(imputer.transform(X_test_raw)) if len(X_test_raw) > 0 else np.array([])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  Device: {device}")

    X_t = torch.FloatTensor(X_train_np).to(device)
    y_t = torch.LongTensor(y_train.values).to(device)

    n_features = X_t.shape[1]
    n_classes = len(ERA_NAMES)

    class EraMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(n_features, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.3),
                nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.2),
                nn.Linear(128, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.1),
                nn.Linear(64, n_classes),
            )
        def forward(self, x):
            return self.net(x)

    model = EraMLP().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    import math as _math
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50)

    # Class weights for imbalance
    class_counts = np.bincount(y_train.values, minlength=n_classes)
    class_weights = torch.FloatTensor(1.0 / (class_counts + 1)).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    dataset = TensorDataset(X_t, y_t)
    loader = DataLoader(dataset, batch_size=256, shuffle=True)

    model.train()
    for epoch in range(50):
        total_loss = 0
        for xb, yb in loader:
            optimizer.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        scheduler.step()
        if (epoch + 1) % 10 == 0:
            print(f"  Epoch {epoch+1}/50 loss={total_loss/len(loader):.4f}")

    model.eval()
    with torch.no_grad():
        train_preds = model(X_t).argmax(dim=1).cpu().numpy()
    train_f1 = f1_score(y_train.values, train_preds, average="macro", zero_division=0)
    print(f"  Train F1-macro: {train_f1:.3f}")

    test_f1 = 0.0
    if len(X_test_np) > 0:
        X_te = torch.FloatTensor(X_test_np).to(device)
        with torch.no_grad():
            test_preds = model(X_te).argmax(dim=1).cpu().numpy()
        test_f1 = f1_score(y_test.values, test_preds, average="macro", zero_division=0)
        print(f"  Test GT F1-macro: {test_f1:.3f}")
        labels_present = sorted(set(y_test.tolist() + test_preds.tolist()))
        print(classification_report(
            y_test.values, test_preds,
            labels=labels_present,
            target_names=[ERA_NAMES[i] for i in labels_present],
            zero_division=0,
        ))

    torch.save({
        "model_state": model.state_dict(),
        "imputer": imputer,
        "scaler": scaler,
        "n_features": n_features,
        "n_classes": n_classes,
        "feature_cols": FEATURE_COLS,
    }, str(BACKEND / "era_model_mlp.pt"))
    print("  Saved: era_model_mlp.pt")

    return model, train_f1, test_f1


def cross_city_eval(pipe, train, test_gt):
    """Per-city breakdown on test GT set."""
    if len(test_gt) == 0:
        print("  No test GT data")
        return
    print("\n=== Cross-City Evaluation ===")
    X_all, y_all = prep(pd.concat([train, test_gt]))

    for city in test_gt["city"].unique():
        city_df = test_gt[test_gt["city"] == city]
        if len(city_df) < 5:
            print(f"  {city}: only {len(city_df)} samples, skipping")
            continue
        X_c, y_c = prep(city_df)
        y_pred = pipe.predict(X_c)
        f1 = f1_score(y_c, y_pred, average="macro", zero_division=0)
        print(f"  {city:12s}: {len(city_df):5d} buildings | F1-macro={f1:.3f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["xgb", "mlp", "both"], default="both")
    parser.add_argument("--eval", action="store_true")
    args = parser.parse_args()

    train, test_gt = load_data()

    best_pipe = None
    best_f1 = -1

    if args.model in ("xgb", "both"):
        pipe_xgb, cv_f1, test_f1 = train_xgboost(train, test_gt)
        if cv_f1 > best_f1:
            best_f1 = cv_f1
            best_pipe = pipe_xgb

    if args.model in ("mlp", "both"):
        _, _, test_f1_mlp = train_mlp(train, test_gt)

    if best_pipe:
        cross_city_eval(best_pipe, train, test_gt)
        with open(BACKEND / "era_model.pkl", "wb") as f:
            pickle.dump(best_pipe, f)
        print(f"\nBest model saved: era_model.pkl (CV F1={best_f1:.3f})")


if __name__ == "__main__":
    main()
