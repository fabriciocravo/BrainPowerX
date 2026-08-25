import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

# return one directory to /brainpowerx/
BASE_DIR = Path(__file__).resolve().parents[2]

# in /brainpowerx/myapp/results
RESULTS_DIR = BASE_DIR / "myapp" / "results"

# glob all directories containing the following - base study
base_study = 'hcp_fc*_t'  # * can be anything


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

# for each of those directories
for study_dir in sorted(RESULTS_DIR.glob(base_study)):
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

    # Get power fit - power_fit_q10, Fast_TFCE
    tfce_fit = get_power_fit(metadata, "power_fit_q10", "Fast_TFCE")

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

    # Parametric_FWER
    # evalute function according to sample size range
    # Plot in left figure
    y_fwer = study["Parametric_FWER"](x)
    ax_left.plot(x, y_fwer, label=study_name)
    lo_fwer = min(lo_fwer, y_fwer.min())
    hi_fwer = max(hi_fwer, y_fwer.max())

    # Fast_TFCE
    # evalute function according to sample size range
    # Plot in right figure
    y_tfce = study["Fast_TFCE"](x)
    ax_right.plot(x, y_tfce, label=study_name)
    lo_tfce = min(lo_tfce, y_tfce.min())
    hi_tfce = max(hi_tfce, y_tfce.max())


# Set axis and plot stuff
ax_left.set_title("Parametric_FWER (q100)")
ax_right.set_title("Fast_TFCE (q10)")
for ax, lo, hi in ((ax_left, lo_fwer, hi_fwer), (ax_right, lo_tfce, hi_tfce)):
    ax.set_xlabel("Sample size")
    pad = 2.5
    ax.set_ylim(lo - pad, hi + pad)
    ax.tick_params(labelleft=True)
ax_left.set_ylabel("Power")
ax_right.legend(fontsize=7)

plt.tight_layout()
plt.show()
