import re, pathlib as P, numpy as np

src = P.Path("gcft00_pk.dat")
out = P.Path("baselines")
out.mkdir(exist_ok=True)
z = None
cur = []
for ln in src.read_text().splitlines():
    s = ln.strip()
    if not s:
        continue
    if s.startswith('#') and 'z =' in s:
        if z is not None and cur:
            arr = np.array([list(map(float, l.split())) for l in cur if l.strip() and not l.startswith('#')])
            out.joinpath(f"gcft00_pk_z{int(z):04d}.dat").write_text(
                "\n".join(" ".join(map("{:.8e}".format, r)) for r in arr) + "\n")
        z = float(re.findall(r'z\s*=\s*([0-9.]+)', s)[0])
        cur = []
    elif not s.startswith('#'):
        cur.append(s)
if z is not None and cur:
    arr = np.array([list(map(float, l.split())) for l in cur if l.strip() and not l.startswith('#')])
    out.joinpath(f"gcft00_pk_z{int(z):04d}.dat").write_text(
        "\n".join(" ".join(map("{:.8e}".format, r)) for r in arr) + "\n")

print("Baselines written to", out)
