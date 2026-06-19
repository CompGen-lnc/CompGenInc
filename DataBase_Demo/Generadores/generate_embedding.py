from pathlib import Path
import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer

BASE = Path(".")
BINDING = BASE / "data" / "binding_zone"
OUT = BASE / "data" / "embedding"
OUT.mkdir(parents=True, exist_ok=True)

texts = []
labels = []
ids = []

def load_folder(folder: Path, label: int):
    for f in sorted(folder.glob("feature_*.txt")):
        txt = f.read_text(errors="ignore")
        txt = "\n".join([l.strip() for l in txt.splitlines() if l.strip()])
        texts.append(txt)
        labels.append(label)
        ids.append(f.stem.replace("feature_", ""))

load_folder(BINDING / "positive_inter", 1)
load_folder(BINDING / "negative_inter", 0)

print(f"Total interacciones: {len(texts)}")

vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3, 5),
    min_df=2,
    max_features=2000
)

X = vectorizer.fit_transform(texts).toarray()

np.save(OUT / "embeddings.npy", X)
np.savetxt(OUT / "labels.txt", labels, fmt="%d")
with open(OUT / "interaction_ids.txt", "w") as f:
    f.write("\n".join(ids))

with open(OUT / "embedding_info.json", "w") as f:
    json.dump({
        "type": "tfidf_char",
        "ngram_range": [3, 5],
        "max_features": 2000,
        "n_samples": len(texts),
        "dim": X.shape[1]
    }, f, indent=2)

print("✅ Embeddings generados:", X.shape)
