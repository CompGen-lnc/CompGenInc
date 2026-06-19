import json
import joblib
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score

THRESHOLD = 0.40
SEED = 42

df = pd.read_csv("binding_features_with_embedding.csv")

base_cols = ["inter_loops","hairpins","multicycles","binding_site_energy","interaction_energy","total_energy"]
emb_cols = [c for c in df.columns if c.startswith("emb_")]
feature_cols = base_cols + emb_cols

X = df[feature_cols].values
y = df["label"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

mlp = MLPClassifier(
    hidden_layer_sizes=(256, 64),
    activation="relu",
    solver="adam",
    alpha=1e-4,
    batch_size=128,
    learning_rate_init=1e-3,
    max_iter=200,
    random_state=SEED,
    early_stopping=True,
    n_iter_no_change=10,
)
mlp.fit(X_train, y_train)

proba = mlp.predict_proba(X_test)[:, 1]
pred = (proba >= THRESHOLD).astype(int)

metrics = {
    "n_samples_total": int(len(df)),
    "n_features": int(len(feature_cols)),
    "seed": SEED,
    "threshold": THRESHOLD,
    "roc_auc": float(roc_auc_score(y_test, proba)),
    "f1": float(f1_score(y_test, pred)),
    "precision": float(precision_score(y_test, pred, zero_division=0)),
    "recall": float(recall_score(y_test, pred, zero_division=0)),
}

out_dir = Path("artifacts")
out_dir.mkdir(exist_ok=True)

joblib.dump(scaler, out_dir / "scaler.joblib")
joblib.dump(mlp, out_dir / "mlp_model.joblib")

with open(out_dir / "model_metadata.json", "w") as f:
    json.dump(metrics, f, indent=2)

with open(out_dir / "feature_columns.txt", "w") as f:
    f.write("\n".join(feature_cols))

print("✅ Guardado en artifacts/: scaler.joblib, mlp_model.joblib, model_metadata.json, feature_columns.txt")
print("📌 Métricas:", metrics)
