import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from color_choice import (
    remove_gt_mat,
    COLOR_DICT,
    TASK_DICT
)

# return one directory to /brainpowerx/
BASE_DIR = Path(__file__).resolve().parents[2]

# in /brainpowerx/myapp/results
RESULTS_DIR = BASE_DIR / "myapp" / "results"

# glob all directories containing the following - base study
# base_study = 'hcp_fc*_t'  # * can be anything
# base_study = 'hcp_act*_t'
# base_study = ["abcd_fc_sex*", "abcd_fc_age*", "abcd_fc_bmi_z*"]
base_study = ["abcd_fc_cbcl_internalizing_r", "abcd_fc_cbcl_externalizing_r", "abcd_fc_cbcl_aggressive_r", "abcd_fc_cbcl_rule_breaking_r", "abcd_fc_cbcl_attention_r", "abcd_fc_cbcl_thought_r", "abcd_fc_cbcl_social_r", "abcd_fc_cbcl_somatic_r", "abcd_fc_cbcl_withdrawn_r", "abcd_fc_cbcl_anx_dep_r"]

# function to read power fit curves
# Signature - metada, method
# Parameters stored as, ex:
# metadata['power_fit_q[quantile_perct']['method']['P']
# Power_fit(x) = P/(1 + (a/x)^b) - return vectorized function
def get_power_fit(metadata, power_fit_name, method):
    params = metadata[power_fit_name][method]
    P, a, b = (
        float(params['P']),
        float(params['a']),
        float(params['b'])
    )

    def power_fit(x):
        x = np.asarray(x, dtype=float)
        return P / (1 + (a / x) ** b)

    return power_fit


# Create dicionary to store results function
results = {}

study_dirs = sorted(set(
    d for pattern in base_study
    for d in RESULTS_DIR.glob(pattern)
))

# for each of those directories
for study_dir in study_dirs:
    if not study_dir.is_dir():
        continue

    # Open metadata.json dictionary
    with open(study_dir / "metadata.json") as f:
        metadata = json.load(f)

    # Get sample size list from metadata
    # metadata["sample_sizes"] - for ploting range
    sample_sizes = metadata["sample_sizes"]

    # Get power fit - power_fit_q100, Parameteric_FWER
    fwer_fit = get_power_fit(metadata, "power_fit_q100", "Parametric_FWER")

    # Get power fit - power_fit_q10, try multiple TFCE method name variants
    for method_name in ("Fast_TFCE_cpp", "IC_TFCE_Node_cpp", "Fast_TFCE"):
        try:
            tfce_fit = get_power_fit(metadata, "power_fit_q10", method_name)
            break
        except KeyError:
            continue
    else:
        raise KeyError(
            "No TFCE method found in power_fit_q10 "
            " for any of the expected method names"
        )

    # Store in dicionary with study name as key
    results[study_dir.name] = {
        "sample_sizes": sample_sizes,
        "Parametric_FWER": fwer_fit,
        "Fast_TFCE": tfce_fit,
    }


# Plot with 2 figures:
fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(10, 4))

lo_fwer, hi_fwer = np.inf, -np.inf
lo_tfce, hi_tfce = np.inf, -np.inf

# for each key in dictionary
for study_name, study in results.items():
    x = np.linspace(
        min(study["sample_sizes"]),
        max(study["sample_sizes"]),
        100
    )

    # Process study name
    key_name = remove_gt_mat(study_name)
    color = COLOR_DICT[key_name]
    label_name = TASK_DICT[key_name]

    # Parametric_FWER
    # evalute function according to sample size range
    # Plot in left figure
    y_fwer = study["Parametric_FWER"](x)
    ax_left.plot(x, y_fwer, color=color, label=label_name)
    lo_fwer = min(lo_fwer, y_fwer.min())
    hi_fwer = max(hi_fwer, y_fwer.max())

    # Fast_TFCE
    # evalute function according to sample size range
    # Plot in right figure
    y_tfce = study["Fast_TFCE"](x)
    ax_right.plot(x, y_tfce, color=color, label=label_name)
    lo_tfce = min(lo_tfce, y_tfce.min())
    hi_tfce = max(hi_tfce, y_tfce.max())


# Set axis and plot stuff
ax_left.set_title("Parametric FWER (q100)")
ax_right.set_title("TFCE (q10)")
for ax, lo, hi in ((ax_left, lo_fwer, hi_fwer), (ax_right, lo_tfce, hi_tfce)):
    ax.set_xlabel("Sample size")
    pad = 2.5
    ax.set_ylim(lo - pad, hi + pad)
    ax.tick_params(labelleft=True)
ax_left.set_ylabel("Power")

if isinstance(base_study, list) and base_study[0] != 'abcd_fc_cbcl_internalizing_r':
    ax_left.legend(fontsize=12)
    ax_right.legend(fontsize=12)
else:
    ax_left.legend(fontsize=8)

plt.tight_layout()
plt.show()
