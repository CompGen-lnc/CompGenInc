import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.linear_model import LogisticRegression

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

clf = LogisticRegression(max_iter=2000)
clf.fit(X_train, y_train)

proba = clf.predict_proba(X_test)[:, 1]
pred = (proba >= 0.5).astype(int)

print("Distribución labels:", df["label"].value_counts().to_dict())
print(classification_report(y_test, pred, digits=4))
print("ROC-AUC:", roc_auc_score(y_test, proba))
