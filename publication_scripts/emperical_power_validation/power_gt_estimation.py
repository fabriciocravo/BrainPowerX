"""
Connected-scatter comparison of subsampled (empirical) vs analytic
ground-truth power curves, one line pair per study/task.
"""

import os
import glob
import json
import colorsys

import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt

# Variable to set quantily percentage
# Either 10, 30, 50 or 100
QUANTILE = 100

# Power directory ./power_data/
POWER_DIR = "./power_data/"
GT_JSON = "./gt_power.json"

# Function to create lighter color for plot
def lighten_color(color, amount=0.6):
    """Blend an RGB(A) color toward white by `amount` (0=no change, 1=white)."""
    r, g, b = color[:3]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = l + (1 - l) * amount
    return colorsys.hls_to_rgb(h, l, s)


# Open gt_power.json - gt_json
with open(GT_JSON, "r") as f:
    gt_json = json.load(f)


# Define function receives meta-data returns study key
def get_study_key(meta_data):
    # Key pattern
    # meta_data.output-meta_data.study_name-meta_data.test_type
    output = str(np.asarray(meta_data.output).ravel()[0])
    study_name = str(np.asarray(meta_data.study_name).ravel()[0])
    test_type = str(np.asarray(meta_data.test_type).ravel()[0])
    return f"{output}-{study_name}-{test_type}"


# Create empty power dicionary
power_dict = {}

# Glob all files from directory
mat_files = sorted(glob.glob(os.path.join(POWER_DIR, "*.mat")))

# For each file in power data
for path in mat_files:
    mat = loadmat(path, squeeze_me=True, struct_as_record=False)
    meta_data = mat["meta_data"]

    # Retrieve key name from meta_data
    key = get_study_key(meta_data)

    # Get subject number from meta_data.n_subs
    n_subs = int(np.asarray(meta_data.n_subs).ravel()[0])

    power_dict.setdefault(key, {"subs": set()})

    # Assign to set of possible subs
    power_dict[key]["subs"].add(n_subs)

    # Get power data vector from Parametric_FWER.tpr
    tpr = np.asarray(mat["Parametric_FWER"].tpr, dtype=float).ravel()

    # Calculate average power according to selected quantile
    # (edges ranked by |effect size|, same convention as the ground-truth
    # script, so the top-QUANTILE% slice lines up with gt_power.json)
    edge_stats = np.asarray(mat["edge_level_stats"], dtype=float).ravel()
    order = np.argsort(np.abs(edge_stats))[::-1]
    m = tpr.size
    k = max(1, int(round(m * QUANTILE / 100.0)))
    slice_idx = order[:k]
    avg_power = float(np.mean(tpr[slice_idx]) * 100)

    # Power dict: Store results in key name (y) and sub number (n)
    power_dict[key]["n" + str(n_subs)] = avg_power


# Color per task, light version for gt, dark version for est
cmap = plt.get_cmap("tab10")
task_colors = {}

fig, ax = plt.subplots(figsize=(7, 5))

# For each key in gt_json
for i, gt_key in enumerate(gt_json):

    # Remove -Ground_Truth from ending
    # ex: hpc_fc_gt-REST_EMOTION-t-Ground_Truth
    key = gt_key.replace("-Ground_Truth", "")

    if key not in power_dict:
        continue

    task_colors[key] = cmap(i % 10)
    dark = task_colors[key]
    light = lighten_color(dark, amount=0.6)

    # Create two lists - gt and subsampled
    ns, gt_vals, sub_vals = [], [], []

    # For each element in the set of possible subs
    for n_subs in sorted(power_dict[key]["subs"]):
        n_key = "n" + str(n_subs)
        q_key = "q" + str(QUANTILE)

        if n_key not in gt_json[gt_key] or q_key not in gt_json[gt_key][n_key]:
            continue
        if n_key not in power_dict[key]:
            continue

        # Get power value
        # gt_json[key]['n'+subnume]['q'+quantile]
        gt_power = gt_json[gt_key][n_key][q_key]

        # Get respective result from power dict
        est_power = power_dict[key][n_key]

        ns.append(n_subs)
        gt_vals.append(gt_power)
        sub_vals.append(est_power)

    if not ns:
        continue

    # plot curve
    ax.plot(ns, gt_vals, marker="o", linestyle="--", color=light)
    ax.plot(ns, sub_vals, marker="o", linestyle="-", color=dark, label=key)

# Legend = task name
ax.set_xlabel("Sample size (N)")
ax.set_ylabel(f"Top-{QUANTILE}% average power (%)")
ax.legend(title="Task (solid=empirical, dashed=analytic)", fontsize=8)
fig.tight_layout()

# Show plot, not save
plt.show()