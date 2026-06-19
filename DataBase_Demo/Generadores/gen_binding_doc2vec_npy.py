"""
gen_binding_doc2vec_npy.py
Genera los tres archivos .npy de embeddings doc2vec por par de interacción:
  - binding_doc2vec_lnc_embeddings.npy
  - binding_doc2vec_mir_embeddings.npy
  - binding_doc2vec_mir_esp_embeddings.npy

Cómo correrlo (desde la carpeta Data_Demo/Generadores/):
  conda activate compgen
  pip install gensim   # si no está instalado
  python gen_binding_doc2vec_npy.py
"""

import numpy as np
import gensim
from pathlib import Path
from tqdm import tqdm

# --- Rutas ---
BASE    = Path(__file__).resolve().parent.parent          # .../Data_Demo
EMB_OUT = BASE / "embedding"
MODELOS = EMB_OUT / "Modelos"

# --- Cargar pares de interacción ---
pos_path = BASE / "interactions/txt_interac_CNN/mirnas_lncrnas_validated_positive_pairs.txt"
neg_path = BASE / "interactions/txt_interac_CNN/negative_pairs.txt"
pos_pairs = [l.strip().split(',') for l in open(pos_path)]
neg_pairs = [l.strip().split(',') for l in open(neg_path)]
all_pairs = pos_pairs + neg_pairs
N = len(all_pairs)
print(f"Total pares: {N}")

# --- Cargar secuencias ---
def read_fa(path):
    seqs = {}
    current_id = None
    for line in open(path):
        line = line.strip()
        if line.startswith('>'):
            current_id = line[1:].split()[0]
        elif current_id:
            seqs[current_id] = line.upper().replace('U', 'T').replace('N', '')
    return seqs

print("Cargando secuencias lncRNA...")
lnc_seqs = read_fa(BASE / "lncRNA/fasta/fasta_seq/outLncRNA_new.fa")

print("Cargando secuencias miRNA...")
mir_seqs = read_fa(BASE / "lncRNA/fasta/fasta_seq/homo_mature_mirna.fa")

# Verificar cobertura
all_lnc = set(p[0] for p in all_pairs)
all_mir = set(p[1] for p in all_pairs)
print(f"Cobertura lnc: {len(all_lnc & set(lnc_seqs))}/{len(all_lnc)}")
print(f"Cobertura mir: {len(all_mir & set(mir_seqs))}/{len(all_mir)}")

# --- Función de segmentación (trinucleótidos) ---
def segment(seq):
    return [seq[i:i+3] for i in range(len(seq) - 2)]

# --- Cargar modelos doc2vec ---
print("\nCargando modelos doc2vec...")
lnc_model     = gensim.models.Doc2Vec.load(str(MODELOS / "lncrna_doc2vec.model"))
mir_model     = gensim.models.Doc2Vec.load(str(MODELOS / "mirna_precursor_doc2vec.model"))
mir_esp_model = gensim.models.Doc2Vec.load(str(MODELOS / "mirna_especifico_doc2vec.model"))
DIM = lnc_model.vector_size
print(f"  Modelos cargados, dim={DIM}")

# --- Función de embedding ---
def embed_seq(model, seq):
    if not seq or len(seq) < 3:
        return np.zeros(model.vector_size, dtype=np.float32)
    model.random.seed(0)
    return model.infer_vector(segment(seq)).astype(np.float32)

# --- Precalcular embeddings únicos (mucho más rápido que por par) ---
print("\nCalculando embeddings únicos de lncRNA...")
lnc_cache = {}
for lnc in tqdm(all_lnc):
    seq = lnc_seqs.get(lnc)
    lnc_cache[lnc] = embed_seq(lnc_model, seq) if seq else np.zeros(DIM, dtype=np.float32)

print("Calculando embeddings únicos de miRNA...")
mir_cache     = {}
mir_esp_cache = {}
for mir in tqdm(all_mir):
    seq = mir_seqs.get(mir)
    if seq:
        mir_cache[mir]     = embed_seq(mir_model, seq)
        mir_esp_cache[mir] = embed_seq(mir_esp_model, seq)
    else:
        mir_cache[mir]     = np.zeros(DIM, dtype=np.float32)
        mir_esp_cache[mir] = np.zeros(DIM, dtype=np.float32)

# --- Ensamblar arrays alineados con all_pairs ---
print("\nEnsamblando arrays...")
lnc_emb     = np.stack([lnc_cache[lnc]     for lnc, _ in all_pairs])
mir_emb     = np.stack([mir_cache[mir]     for _, mir in all_pairs])
mir_esp_emb = np.stack([mir_esp_cache[mir] for _, mir in all_pairs])

# --- Guardar ---
np.save(EMB_OUT / "binding_doc2vec_lnc_embeddings.npy",     lnc_emb)
np.save(EMB_OUT / "binding_doc2vec_mir_embeddings.npy",     mir_emb)
np.save(EMB_OUT / "binding_doc2vec_mir_esp_embeddings.npy", mir_esp_emb)

print(f"\n✅ Guardados en {EMB_OUT}:")
print(f"  binding_doc2vec_lnc_embeddings.npy:     {lnc_emb.shape}")
print(f"  binding_doc2vec_mir_embeddings.npy:     {mir_emb.shape}")
print(f"  binding_doc2vec_mir_esp_embeddings.npy: {mir_esp_emb.shape}")
