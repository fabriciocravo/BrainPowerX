from pathlib import Path
from scipy.io import loadmat
from scipy.optimize import curve_fit
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict

raise ValueError('This script is current being accessed for usage. '
                 'I decided to move plotting generation to matlab to avoid major issues')

# ─────────────────────────────────────────────
#  MATRIX RECONSTRUCTION
#  Equivalent of roi_roi_unflat.m:
#    temp_y = zeros(size(mask))
#    temp_y(mask) = flat_matrix
#    unflat_matrix = temp_y + temp_y'
# ─────────────────────────────────────────────
def roi_roi_unflat(flat_matrix, mask):
    temp_y = np.zeros(mask.shape, dtype=float)
    temp_y[mask.astype(bool)] = flat_matrix
    return temp_y + temp_y.T

# ─────────────────────────────────────────────
#  POWER CURVE  P / (1 + (a/n)^b)
# ─────────────────────────────────────────────
def power_curve(n, P, a, b):
    return P / (1.0 + (a / n) ** b)

def fit_power_curve(ns, powers):
    valid = ~np.isnan(powers)
    if valid.sum() < 3:
        return None
    try:
        popt, _ = curve_fit(
            power_curve,
            ns[valid], powers[valid],
            p0=[100, np.median(ns), 2],
            bounds=([0, 0, 0.1], [100, 1e4, 20]),
            maxfev=10_000,
        )
        n_dense = np.linspace(ns[valid].min(), ns[valid].max() * 2, 300)
        return popt, n_dense, power_curve(n_dense, *popt)
    except Exception:
        return None

# ─────────────────────────────────────────────
#  FILENAME PARSER
#  pr-{dataset}_{map}-{task}-{test}-subs_{n}.mat
# ─────────────────────────────────────────────
def parse_filename(path: Path):
    parts    = path.stem.split("-")
    ds_map   = parts[1]
    task     = parts[2]
    test     = parts[3]
    n_subs   = int(parts[4].split("_")[1])
    first_us = ds_map.index("_")
    dataset  = ds_map[:first_us]
    map_type = ds_map[first_us + 1:]
    return dataset, map_type, task, test, n_subs

# ─────────────────────────────────────────────
#  DATA EXTRACTORS
# ─────────────────────────────────────────────
def extract_power(data, method):
    inner = data[method][0][0]
    return inner[2].flatten().astype(float)

def extract_meta(data):
    meta        = data["meta_data"][0][0]
    mask        = meta["mask"][0][0].astype(bool)
    edge_groups = meta["edge_groups"][0][0].astype(float)
    return mask, edge_groups
