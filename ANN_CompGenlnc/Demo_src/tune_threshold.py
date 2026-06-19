import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score

df = pd.read_csv("binding_features_demo.csv")
X = df[["inter_loops","hairpins","multicycles","binding_site_energy","interaction_energy","total_energy"]].values
y = df["label"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

mlp = MLPClassifier(
    hidden_layer_sizes=(64, 32, 16),
    activation="relu",
    solver="adam",
    alpha=1e-4,
    batch_size=64,
    learning_rate_init=1e-3,
    max_iter=500,
    random_state=42,
    early_stopping=True,
    n_iter_no_change=20,
)
mlp.fit(X_train, y_train)

proba = mlp.predict_proba(X_test)[:, 1]
print("ROC-AUC:", roc_auc_score(y_test, proba))

best = None
for t in np.linspace(0.1, 0.9, 17):
    pred = (proba >= t).astype(int)
    f1 = f1_score(y_test, pred)
    p = precision_score(y_test, pred, zero_division=0)
    r = recall_score(y_test, pred, zero_division=0)
    row = (f1, t, p, r)
    if best is None or row[0] > best[0]:
        best = row

print(f"Mejor F1={best[0]:.4f} con threshold={best[1]:.2f} | precision={best[2]:.4f} recall={best[3]:.4f}")
