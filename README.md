# GCFT Power Spectrum Simulation Release

This package contains the data, figures, and manuscript for the paper:

**"Power Spectrum Predictions from General Coherence Field Theory: Implementation and Comparison with ΛCDM"**  
Author: Nick Hacquier  
Affiliation: Aporion Dynamics

---

## Contents

- `main.pdf` — Compiled manuscript.  
- `main.tex` — LaTeX source of the manuscript.  
- `fig1_gcft_vs_lcdm.png` — Power spectrum comparison between GCFT and ΛCDM.  
- `fig2_relative_diff.png` — Relative deviation of GCFT from ΛCDM.  
- `GCFT00_pk.dat` — GCFT simulation output: matter power spectrum.  
- `requirements.txt` — Python package dependencies for included scripts.  
- `reproduce.sh` — Script to compile CLASS and run the simulation using `gcft.ini`.  
- (Add any plotting or analysis scripts you wish to share.)

---

## Description

This dataset presents cosmological simulation results for the General Coherence Field Theory (GCFT), implemented in a modified CLASS Boltzmann code. The provided manuscript details the theoretical background, numerical methods, and resulting power spectrum comparison with standard ΛCDM cosmology.

**Highlights:**  
- GCFT reproduces ΛCDM at large scales but predicts small-scale power suppression.  
- All key data and figures are included for verification and further analysis.

---

## How to Use

- **Paper**: Read `main.pdf` for full context and results.  
- **Data**: Use `GCFT00_pk.dat` for custom analysis or to reproduce figures.  
- **Figures**: Included PNGs correspond to those referenced in the manuscript.  
- **Reproduction**: Run `./reproduce.sh` to compile CLASS and execute the simulation using `gcft.ini`. Ensure you have necessary build tools installed.  
- **Python Scripts**: If provided, install dependencies via `pip install -r requirements.txt` to run any included analysis or plotting scripts.

---

## Requirements

Minimum Python packages required for analysis and plotting:  
- numpy  
- scipy  
- matplotlib  
- cython (if building the CLASS Python wrapper)

Install all with:  
```bash
pip install -r requirements.txt
