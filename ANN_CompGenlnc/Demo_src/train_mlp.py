import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.neural_network import MLPClassifier

df = pd.read_csv("binding_features_demo.csv")

X = df[[
    "inter_loops","hairpins","multicycles",
    "binding_site_energy","interaction_energy","total_energy"
]].values
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
pred = (proba >= 0.5).astype(int)

print("Distribución labels:", df["label"].value_counts().to_dict())
print(classification_report(y_test, pred, digits=4))
print("ROC-AUC:", roc_auc_score(y_test, proba))
