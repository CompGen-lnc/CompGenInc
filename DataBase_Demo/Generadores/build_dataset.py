import re
from pathlib import Path
import openpyxl
import pandas as pd

BASE = Path(".")
LOOPS_DIR = BASE / "data" / "ss_loops"
MIR_POS = BASE / "miranda_binding_calc" / "binding_site_positive"
MIR_NEG = BASE / "miranda_binding_calc" / "binding_site_negative"

ENERGY_TOTAL_RE = re.compile(r"\((-?\d+(?:\.\d+)?)\)\s*$")
LINE_RE = re.compile(
    r"^(External loop|Interior loop|Hairpin\s+loop|Multi\s+loop)\s*\((\d+),(\d+)\).*?:\s*([+-]?\d+)\s*$"
)
HIT_RE = re.compile(
    r"Forward:.*?R:(\d+)\s+to\s+(\d+).*?Energy:\s*(-?\d+(?:\.\d+)?)\s*kCal/Mol",
    re.S
)

def parse_miranda(path: Path):
    txt = path.read_text(errors="ignore")
    hits = [(int(a), int(b), float(e)) for a, b, e in HIT_RE.findall(txt)]
    if not hits:
        return None
    return min(hits, key=lambda x: x[2])  # energía más negativa

def parse_loops(lnc: str):
    fp = LOOPS_DIR / f"loops_{lnc}.txt"
    if not fp.exists():
        return None

    lines = fp.read_text(errors="ignore").splitlines()

    total_energy = None
    for line in reversed(lines):
        m = ENERGY_TOTAL_RE.search(line.strip())
        if m:
            total_energy = float(m.group(1))
            break

    events = []
    for line in lines:
        m = LINE_RE.match(line.strip())
        if not m:
            continue
        kind, a, b, e = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
        events.append((kind, a, b, e))

    return {"total_energy": total_energy, "events": events}

def in_range(a, b, R1, R2):
    lo, hi = sorted((a, b))
    return (lo >= R1) and (hi <= R2)

def features_for_pair(lnc: str, mir: str, mir_path: Path):
    loops = parse_loops(lnc)
    if loops is None or loops["total_energy"] is None:
        return None

    hit = parse_miranda(mir_path)
    if hit is None:
        return {
            "name": f"{lnc}_{mir}",
            "inter_loops": 0,
            "hairpins": 0,
            "multicycles": 0,
            "binding_site_energy": 0.0,
            "interaction_energy": 0.0,
            "total_energy": loops["total_energy"],
        }

    R1, R2, e_inter = hit
    inter_loops = hairpins = multicycles = 0
    bind_sum = 0

    for kind, a, b, e in loops["events"]:
        if not in_range(a, b, R1, R2):
            continue
        if kind == "Interior loop":
            inter_loops += 1
        elif kind.startswith("Hairpin"):
            hairpins += 1
        elif kind.startswith("Multi"):
            multicycles += 1
        bind_sum += e

    return {
        "name": f"{lnc}_{mir}",
        "inter_loops": inter_loops,
        "hairpins": hairpins,
        "multicycles": multicycles,
        "binding_site_energy": bind_sum / 100.0,
        "interaction_energy": e_inter,
        "total_energy": loops["total_energy"],
    }

def main():
    wb = openpyxl.load_workbook(BASE / "Interactions.xlsx", data_only=True)
    rows = []
    skipped_loops = 0
    skipped_mir = 0

    for sheet_name, label in [("Positive", 1), ("Negative", 0)]:
        ws = wb[sheet_name]
        for r in ws.iter_rows(min_row=2, values_only=True):
            lnc, mir, _, fname = r
            if not lnc or not mir or not fname:
                continue

            fname = str(fname).strip()
            mir_path = (MIR_POS if label == 1 else MIR_NEG) / fname
            if not mir_path.exists():
                skipped_mir += 1
                continue

            feat = features_for_pair(str(lnc).strip(), str(mir).strip(), mir_path)
            if feat is None:
                skipped_loops += 1
                continue

            feat["label"] = label
            rows.append(feat)

    df = pd.DataFrame(rows)
    df.to_csv("binding_features_demo.csv", index=False)
    print("✅ Listo: binding_features_demo.csv")
    print(f"Filas: {len(df)} | Omitidas (loops faltantes): {skipped_loops} | Omitidas (miranda faltante): {skipped_mir}")
    print(df.head(5).to_string(index=False))

if __name__ == "__main__":
    main()
