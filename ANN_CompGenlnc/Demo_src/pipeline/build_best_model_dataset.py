from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(".")
EMB_DIR = BASE / "data" / "embedding"

# 1) Cargar embeddings + ids + labels
X_emb = np.load(EMB_DIR / "embeddings.npy")           # (N, D)
ids = (EMB_DIR / "interaction_ids.txt").read_text().splitlines()
y = np.loadtxt(EMB_DIR / "labels.txt", dtype=int)

assert len(ids) == X_emb.shape[0] == len(y), "Inconsistencia entre embeddings/ids/labels"

emb_cols = [f"emb_{i}" for i in range(X_emb.shape[1])]
df_emb = pd.DataFrame(X_emb, columns=emb_cols)
df_emb["name"] = ids
df_emb["label_emb"] = y

# 2) Cargar features clásicas (6 features + label)
df_base = pd.read_csv("binding_features_demo.csv")

# 3) Unir por 'name' (interacción)
df = df_base.merge(df_emb, on="name", how="inner")

# 4) Validaciones rápidas
print("Base:", df_base.shape, "Emb:", df_emb.shape, "Merged:", df.shape)

# Si hay discrepancias, lo mostramos
missing_in_base = set(ids) - set(df_base["name"].tolist())
if missing_in_base:
    print("⚠️ Interacciones con embedding que NO están en binding_features_demo.csv:", len(missing_in_base))

# Asegurar que label coincide
if "label" in df.columns and "label_emb" in df.columns:
    mismatch = (df["label"] != df["label_emb"]).sum()
    print("Mismatches label:", mismatch)
    df = df.drop(columns=["label_emb"])

# 5) Guardar dataset final
out = BASE / "binding_features_with_embedding.csv"
df.to_csv(out, index=False)
print("✅ Listo:", out, "| shape:", df.shape)
