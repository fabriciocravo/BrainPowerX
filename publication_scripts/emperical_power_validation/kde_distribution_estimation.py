import glob
import pickle

import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
from pymatreader import read_mat
import os


# Function to get parameter from mat file
def get_param_from_mat(mat_file, parameter):
    data = read_mat(mat_file)
    return data[parameter]


fig_x = 3.5
fig_y = 2.2

# Data in './distribution_fit_data/' - mat files
# Glob files open in file_mats
file_mats = glob.glob("./distribution_fit_data/*.mat")

kde_dict = {}

# For each matfile
for mat in file_mats:

    # From matfile in meta_data
    meta_data = get_param_from_mat(mat, "meta_data")
    test_type = meta_data["test_type"]

    # Get t-stats
    t_stats = get_param_from_mat(mat, "edge_level_stats")

    # Convert t-stats to np array
    t_stats = np.asarray(t_stats)

    if test_type == "t":
        n = meta_data["n_subs"]
        denominator = np.sqrt(n)

    # If t2 - n1 = n_subs_1, n2 = n_subs_2
    elif test_type == "t2":
        n1 = meta_data["n_subs_1"]
        n2 = meta_data["n_subs_2"]
        n = n1 + n2
        denominator = np.sqrt((n1 * n2) / (n1 + n2))

    elif test_type == "r":
        n = meta_data["n_subs"]
        df = n - 2
        r = t_stats / np.sqrt(t_stats**2 + df)      # t -> r
        ef_sizes = 2 * r / np.sqrt(1 - r**2)        # r -> d

    else:
        raise ValueError(
            f"Unknown test_type '{test_type}' in {mat}"
        )

    n_var = len(t_stats)

    # Calculate effect sizes
    if test_type != "r":
        ef_sizes = t_stats / denominator

    # Get distribution KDE - gaussian
    kde = gaussian_kde(ef_sizes)

    # Get basename
    base_name = os.path.basename(mat)

    # Add KDE object to dictionary
    # Key file name - value KDE object
    kde_dict[base_name] = {'kde': kde, 'n_subs': n, 'n_var': n_var}


# Pickle save the dictionary in '/distribution_fit_data/'
with open("./distribution_fit_data/kde_fit.pkl", "wb") as f:
    pickle.dump(kde_dict, f)



# Map filename substrings to short, human-readable labels
NAME_MAP = {
    "abcd_fc_gt-test1-t2-Ground_Truth.mat": "ABCD FC - Gender",
    "abcd_fc_gt-test14-r-Ground_Truth.mat": "ABCD FC - Depression/Anxiety",
    "hcp_activation-WM-t-Ground_Truth.mat": "HCP Activation - Working Memory",
    "hpc_fc_gt-REST_GAMBLING-t-Ground_Truth.mat": "HCP FC - Gambling",
}

n_keys = len(kde_dict)

# Number of columns in the grid
n_cols = 2
n_rows = int(np.ceil(n_keys / n_cols))

fig, axes = plt.subplots(
    n_rows,
    n_cols,
    figsize=(fig_x * n_cols, fig_y * n_rows)
)
axes = np.atleast_2d(axes).flatten()

# For each key in the KDE dictionary
for ax, (name, entry) in zip(axes, kde_dict.items()):
    kde = entry["kde"]
    n_subs = entry["n_subs"]

    # Plot the pdf of the KDE
    x = np.linspace(
        np.percentile(kde.dataset, 2.5),
        np.percentile(kde.dataset, 97.5),
        500
    )
    ax.plot(x, kde(x))

    name = NAME_MAP[name]
    ax.set_title(f"{name} (n={n_subs})")

# Hide any unused subplots (when n_keys isn't a perfect multiple of n_cols)
for ax in axes[n_keys:]:
    ax.axis("off")

plt.tight_layout()
plt.show()

