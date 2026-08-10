"""
Analytic (closed-form) power estimation from full-dataset t-statistics.

For each ground-truth .mat file, rescale the reference t-stats to a target
sample size, compute per-edge power under a Bonferroni-corrected one-sided
t-test taken in the direction of the ground-truth sign, and average power
within the top-X% of edges ranked by |effect|.
"""

import os
import glob
import json

import numpy as np
from scipy import stats
from scipy.io import loadmat

# ---------------------------------------------------------------- settings ---
GT_DIR = "./gt_data/"
OUT_JSON = "./gt_power.json"
SAMPLE_SIZES = [20, 40, 80, 120, 200]
Q_PERCENTAGES = [10, 30, 50, 100]
ALPHA = 0.05


def load_mat_fields(path):
    """Pull edge_level_stats and meta_data.n_subs out of a .mat file."""
    mat = loadmat(path, squeeze_me=True, struct_as_record=False)
    # Ravel converts from (n, 1) and (1, n) to (n,)
    t_ref = np.asarray(mat["edge_level_stats"], dtype=float).ravel()
    meta = mat["meta_data"]
    n_ref = int(np.asarray(meta.n_subs).ravel()[0])
    return t_ref, n_ref

    
def power_at_n(t_ref, n_ref, n, alpha=ALPHA):
    """Per-edge power at sample size n, Bonferroni-corrected over all edges.

    One-sided test taken in the direction of the ground-truth sign. Because
    nct.sf(c, df, d) == nct.cdf(-c, df, -d), the signed test on a negative
    effect has the same power as the positive-direction test on |delta|.
    """
    m = t_ref.size
    df = n - 1
    delta = np.abs(t_ref) * np.sqrt(n / n_ref)   
    t_crit = stats.t.isf(alpha / m, df)          # Bonferroni
    return stats.nct.sf(t_crit, df, delta)


# Get all mat files names in ./gt_data/
# Each file is a .mat file
mat_files = sorted(glob.glob(os.path.join(GT_DIR, "*.mat")))

# create empty results dictionary
results = {}

# for each file in ./gt_data/
for path in mat_files:
    file_key = os.path.splitext(os.path.basename(path))[0]

    # edge_level_stats contains the t-stats
    # meta_data.n_subs contains the number os subjects
    t_ref, n_ref = load_mat_fields(path)

    # rank edges once by dataset effect ranking is N-invariant because
    # the sqrt(N) rescaling is a monotone transform applied to every edge
    order = np.argsort(np.abs(t_ref))[::-1]
    m = t_ref.size

    results[file_key] = {}

    # recale t-stat to sample sizes - (delta = t_ref * sqrt(N / N_ref))
    # for each sample size
    for n in SAMPLE_SIZES:

        # estimate power of all effects
        power = power_at_n(t_ref, n_ref, n)

        results[file_key]['n'+str(n)] = {}

        # calculate the average powers
        # for the top10%, top30%, top50%, 100%
        for q in Q_PERCENTAGES:
            k = max(1, int(round(m * q / 100.0)))
            slice_idx = order[:k]

            # store in results dictonary
            # first key is file name (no ext)
            # second key is sample size
            # third key is percentaly qPercentage
            mean_p = float(np.mean(power[slice_idx])*100)
            results[file_key]['n'+str(n)]['q'+str(q)] = mean_p

# Save results to json file
with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=2)

print(f"Wrote {OUT_JSON}: {len(results)} files x {len(SAMPLE_SIZES)} sample sizes")


