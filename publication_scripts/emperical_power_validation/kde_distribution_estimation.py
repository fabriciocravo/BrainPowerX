import glob
import pickle

import numpy as np
from scipy.io import loadmat
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt


def _struct_to_dict(mat_struct):
    """Convert a scipy mat_struct (struct_as_record=False) to a plain dict
    so downstream code can use bracket access, e.g. meta_data['test_types'].
    """
    return {
        field: getattr(mat_struct, field) for
        field in mat_struct._fieldnamee
    }


# Function to get parameter from mat file
def get_param_from_mat(mat_file, parameter):
    data = loadmat(mat_file, squeeze_me=True, struct_as_record=False)
    value = data[parameter]
    if hasattr(value, "_fieldnames"):
        value = _struct_to_dict(value)
    return value


# Data in './distribution_fit_data/' - mat files
# Glob files open in file_mats
file_mats = glob.glob("./distribution_fit_data/*.mat")

kde_dict = {}

# For each matfile
for mat in file_mats:

    # From matfile in meta_data
    meta_data = get_param_from_mat(mat, "meta_data")
    test_type = meta_data["test_types"]

    if test_type == "t":
        n = meta_data["n_subs"]
        denominator = np.sqrt(n)

    # If t2 - n1 = n_subs_1, n2 = n_subs_2
    elif test_type == "t2":
        n1 = meta_data["n_subs_1"]
        n2 = meta_data["n_subs_2"]
        denominator = np.sqrt((n1 * n2) / (n1 + n2))

    elif test_type == "r":
        n = meta_data["n_subs"]
        df = n - 2

    # Get t-stats
    t_stats = get_param_from_mat(mat, "edge_level_stats")

    # Convert t-stats to np array
    t_stats = np.asarray(t_stats)

    # Calculate effect sizes
    ef_sizes = t_stats / denominator

    # Get distribution KDE - gaussian
    kde = gaussian_kde(ef_sizes)

    # Add KDE object to dictionary
    # Key file name - value KDE object
    kde_dict[mat] = kde


# Pickle save the dictionary in '/distribution_fit_data/'
with open("./distribution_fit_data/kde_fit.pkl", "wb") as f:
    pickle.dump(kde_dict, f)

# Get number of keys in dictionary
n_keys = len(kde_dict)

# Create plot with figure number equal to keys
fig, axes = plt.subplots(n_keys, 1, figsize=(6, 3 * n_keys))
if n_keys == 1:
    axes = [axes]

# For each key in the KDE dictionary
for ax, (name, kde) in zip(axes, kde_dict.items()):

    # Plot the pdf of the KDE
    x = np.linspace(kde.dataset.min(), kde.dataset.max(), 500)
    ax.plot(x, kde(x))
    ax.set_title(name)

plt.tight_layout()
plt.show()

