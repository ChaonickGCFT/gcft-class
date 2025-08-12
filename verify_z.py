#!/usr/bin/env python3
# verify_z.py — compare new z-scan P(k) outputs against baselines
import re, sys, math, pathlib as P
import numpy as np

OUT_DIR = P.Path("output")
NEW_PREFIX = "gcft_zscan"            # what your workflow renames outputs to
BASELINES_DIR = P.Path("baselines")  # optional per-z baselines live here
BASELINE_COMBINED = P.Path("gcft00_pk.dat")  # optional combined baseline in repo root

TOL = 5e-6  # relative tolerance

_num = re.compile(r'^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$')

def load_table(path: P.Path):
    rows = []
    with open(path, 'r', errors='ignore') as f:
        for s in (ln.strip() for ln in f):
            if not s or s.startswith('#'):
                continue
            cols = s.split()
            if len(cols) >= 2 and _num.match(cols[0]) and _num.match(cols[1]):
                rows.append([float(cols[0]), float(cols[1])])
    return np.array(rows, float)

def read_pk_blocks_combined(path: P.Path):
    """Parse a combined *_pk.dat with '# z = ...' sections -> {z: (k, Pk)}"""
    blocks = {}
    z = None
    k, pk = [], []
    with open(path, "r", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#") and "z =" in s:
                if z is not None and k:
                    blocks[z] = (np.array(k), np.array(pk))
                k, pk = [], []
                try:
                    z = float(s.split("z =", 1)[1].split()[0].replace(",", ""))
                except Exception:
                    z = None
                continue
            if not s.startswith("#"):
                cols = s.split()
                if len(cols) >= 2 and _num.match(cols[0]) and _num.match(cols[1]):
                    k.append(float(cols[0])); pk.append(float(cols[1]))
    if z is not None and k:
        blocks[z] = (np.array(k), np.array(pk))
    return blocks

def read_pk_file_per_z(path: P.Path):
    """Parse a per-z file (no headers) -> (k, Pk)"""
    A = load_table(path)
    if A.size == 0 or A.shape[1] < 2:
        return None
    return A[:, 0], A[:, 1]

def z_from_fname(path: P.Path):
    """Extract z from name like *_pk_z0025.dat -> 25.0"""
    m = re.search(r'_z(\d{4})\.dat$', path.name)
    if not m:
        return None
    return float(int(m.group(1)))

def max_rel(a, b):
    return float(np.nanmax(np.abs(a - b) / np.maximum(np.abs(b), 1e-12)))

def gather_new_blocks():
    # Prefer per-z files
    perz = sorted(OUT_DIR.glob(f"{NEW_PREFIX}_pk_z*.dat"))
    blocks = {}
    if perz:
        for p in perz:
            z = z_from_fname(p)
            if z is None:
                continue
            kb = read_pk_file_per_z(p)
            if kb is None:
                continue
            blocks[z] = kb
        return blocks
    # Fallback: combined file
    combined = OUT_DIR / f"{NEW_PREFIX}_pk.dat"
    if combined.exists():
        return read_pk_blocks_combined(combined)
    return {}

def gather_baseline_blocks():
    # Prefer per-z baselines
    perz = sorted(BASELINES_DIR.glob("gcft00_pk_z*.dat"))
    blocks = {}
    if perz:
        for p in perz:
            z = z_from_fname(p)
            if z is None:
                continue
            kb = read_pk_file_per_z(p)
            if kb is None:
                continue
            blocks[z] = kb
        return blocks
    # Fallback: combined baseline
    if BASELINE_COMBINED.exists():
        return read_pk_blocks_combined(BASELINE_COMBINED)
    return {}

def main():
    new_blocks = gather_new_blocks()
    if not new_blocks:
        print("[FAIL] No new gcft_zscan pk outputs found in 'output/'.")
        sys.exit(1)

    base_blocks = gather_baseline_blocks()
    if not base_blocks:
        print("[WARN] No baselines found (neither baselines/gcft00_pk_z*.dat nor gcft00_pk.dat). Skipping verification.")
        sys.exit(0)

    z_new   = sorted(new_blocks.keys())
    z_base  = sorted(base_blocks.keys())
    commonZ = [z for z in z_new if z in z_base]

    if not commonZ:
        print(f"[FAIL] No common redshifts. New={z_new} vs Base={z_base}")
        sys.exit(1)

    ok = True
    for z in commonZ:
        kN, PN = new_blocks[z]
        kB, PB = base_blocks[z]

        # Compare on baseline k-grid overlap
        kmin, kmax = max(kN.min(), kB.min()), min(kN.max(), kB.max())
        mask = (kB >= kmin) & (kB <= kmax)
        if not np.any(mask):
            print(f"[FAIL] z={z:g}: no overlapping k-range.")
            ok = False
            continue

        # Dedup kN for interpolation
        kNu, idx = np.unique(kN, return_index=True)
        PNu = PN[idx]
        PNi = np.interp(kB[mask], kNu, PNu)

        diff = max_rel(PNi, PB[mask])
        tag = "OK" if diff <= TOL else "FAIL"
        print(f"[{tag}] Pk @ z={z:g}: max rel diff = {diff:.3e} (tol={TOL:.1e})")
        ok &= (diff <= TOL)

    missing_in_base = [z for z in z_new if z not in z_base]
    missing_in_new  = [z for z in z_base if z not in z_new]
    if missing_in_base:
        print(f"[INFO] New-only z: {missing_in_base}")
    if missing_in_new:
        print(f"[INFO] Baseline-only z: {missing_in_new}")

    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
