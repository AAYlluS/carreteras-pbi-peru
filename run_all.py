"""Produce every table, figure and the paper with one command.

    python run_all.py              # full pipeline
    python run_all.py --skip-gis   # skip the maps

Steps run in order; each step reads only data/raw, the Seminario & Palomino
workbook downloaded by step 0 into data/external, and the outputs of earlier
steps. data/processed and output/tables are rebuilt from scratch on every run;
the maps in output/figures are overwritten (a map whose inputs are missing is
kept as committed).
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = [
    ("00_get_gdp.py", "download Seminario & Palomino district GDP", False),
    ("01_clean.py", "build analysis samples", False),
    ("02_analysis.py", "Tables 1-3", False),
    ("03_spatial.py", "Tables 4-5 (spatial)", False),
    ("04_inference.py", "Table 6 (what the 2SLS estimate rules out)", False),
    ("05_figures.py", "Figures 1-4 (maps)", True),
    ("06_working_paper.py", "working paper HTML/PDF", False),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-gis", action="store_true", help="skip the maps")
    args = ap.parse_args()

    for d in ("data/processed", "output/tables"):
        shutil.rmtree(ROOT / d, ignore_errors=True)
        (ROOT / d).mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    for script, desc, gis in STEPS:
        if gis and args.skip_gis:
            print(f"--- skip {script} ({desc})")
            continue
        print(f"=== {script}: {desc}", flush=True)
        t = time.time()
        subprocess.run([sys.executable, str(ROOT / "code" / script)], cwd=ROOT, check=True)
        print(f"    done in {time.time() - t:.1f} s", flush=True)
    print(f"All steps finished in {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
