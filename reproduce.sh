#!/usr/bin/env bash
set -euo pipefail
set -x  # Enable debugging output

# --- config ---
BG_FILE=${BG_FILE:-gcft_class_background.dat}   # must exist next to this script
CLASS_BIN=./class
MAKE_J=$(command -v nproc >/dev/null 2>&1 && nproc || echo 2)

# Candidates for the high-z probe (highest first)
ZCAND=("2000" "1500" "1200" "1100" "1000" "800" "600" "400" "300" "200" "100" "50" "25" "10")

# Logging function
log() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

log "==> Compiling CLASS…"
make -j"${MAKE_J}"

# Check if CLASS binary exists and is executable
if [[ ! -x "$CLASS_BIN" ]]; then
  log "ERROR: $CLASS_BIN not found/exec."
  exit 1
fi

# Check if background file exists
if [[ ! -f "$BG_FILE" ]]; then
  log "ERROR: Background table '$BG_FILE' not found."
  exit 1
fi

# Create necessary directories and clean output
mkdir -p results logs
rm -f output/* 2>/dev/null || true

# ---------- A) High-z mPk only (auto-probe z) ----------
log "==> Phase A: high-z mPk (no CMB), probing for highest stable z_pk…"

# Template (Z_HI will be substituted)
read -r -d '' INI_A_TPL <<'INI'
output = mPk
l_max_scalars = 1
P_k_max_h/Mpc = 10
z_pk = 0, 25, Z_HI
matter_source_in_current_gauge = yes

use_tabulated_background = yes
background_filename = __BG__

k_pivot = 0.05
P_k_ini type = analytic_Pk
A_s = 2.1e-9
n_s = 0.965

reionization = yes
re_use_optical_depth = yes
tau_reio = 0.054

write background = yes
write thermodynamics = yes
write pk = yes

perturbations_verbose = 1
background_verbose = 1
INI

FOUND_Z=""
# Disable parallel execution for debugging
log "==> Starting z_pk probing…"
for Z in "${ZCAND[@]}"; do
  INI_A=$(echo "$INI_A_TPL" | sed -e "s/Z_HI/$Z/g" -e "s|__BG__|$BG_FILE|g")
  echo "$INI_A" > gcft_zlimit_highz_${Z}.ini

  log " -> trying z_pk=$Z …"
  if "$CLASS_BIN" gcft_zlimit_highz_${Z}.ini >"logs/highz_${Z}.log" 2>&1; then
    FOUND_Z="$Z"
    log "    ✓ success at z_pk=$FOUND_Z"
    break
  else
    log "    ✗ failed at z_pk=$Z (see logs/highz_${Z}.log). Trying lower…"
    rm -f output/* 2>/dev/null || true
  fi
done

# If no valid z_pk found, log and exit
if [[ -z "$FOUND_Z" ]]; then
  log "ERROR: All candidate redshifts failed in Phase A."
  for Z in "${ZCAND[@]}"; do
    if [[ ! -f "logs/highz_${Z}.log" ]]; then
      log "No log found for z_pk=$Z"
    fi
  done
  exit 1
fi

# stash A outputs
for f in output/*; do
  b=$(basename "$f")
  cp "$f" "results/highz_z${FOUND_Z}_$b"
done
rm -f output/* 2>/dev/null || true

# ---------- B) CMB only ----------
log "==> Phase B: CMB only (no mPk)…"

cat > gcft_zlimit_cmb.ini <<EOF
output = tCl, lCl, pCl
l_max_scalars = 2500
P_k_max_h/Mpc = 5
# harmless z list when no mPk is requested
z_pk = 0, 1, 2

use_tabulated_background = yes
background_filename = $BG_FILE

k_pivot = 0.05
P_k_ini type = analytic_Pk
A_s = 2.1e-9
n_s = 0.965

reionization = yes
re_use_optical_depth = yes
tau_reio = 0.054

write background = yes
write thermodynamics = yes
write cl = yes

perturbations_verbose = 1
background_verbose = 1
EOF

"$CLASS_BIN" gcft_zlimit_cmb.ini >"logs/cmb.log" 2>&1

# stash B outputs
for f in output/*; do
  b=$(basename "$f")
  cp "$f" "results/cmb_$b"
done

log "==> Done."
log "   Phase A highest stable z_pk: $FOUND_Z"
log "   Results saved under: $(pwd)/results"
log "   Logs in: $(pwd)/logs"
