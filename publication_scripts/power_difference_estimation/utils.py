import numpy as np
from pymatreader import read_mat
from scipy import stats


def get_param_from_mat(mat_file, parameter):
    data = read_mat(mat_file)
    return data[parameter]


def convert_t_stats(t_stats, meta_data):

    test_type = meta_data["test_type"]

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
        return ef_sizes

    else:
        raise ValueError(
            f"Unknown test_type {test_type}"
        )

    ef_sizes = t_stats / denominator

    return ef_sizes


def calculate_power_curve(
        centrality,
        n_var,
        n_sub_range,
        alpha,
        skip_range=20,
):

    if centrality < 0:
        raise ValueError(
            'Function calculate_power_curve '
            'designed for only positive absolute effect sizes'
        )

    sub_array = np.arange(20, n_sub_range + 1, skip_range)
    power_array = np.zeros(sub_array.size)

    # Calculate power from true effect for each true effect - 2 sided
    for i, n_sub in enumerate(sub_array):

        df = n_sub - 1
        t_crit = stats.t.ppf(1 - alpha / (2 * n_var), df)
        ncp = centrality * np.sqrt(n_sub)

        # Break the integral due to numerical instability
        cdf_pos = stats.nct.cdf(t_crit, df, ncp)
        cdf_neg = stats.nct.cdf(-t_crit, df, ncp)

        # Solve numerical instabilities
        cdf_pos = np.where(np.isnan(cdf_pos), 1.0, cdf_pos)
        cdf_neg = np.where(np.isnan(cdf_neg), 0.0, cdf_neg)

        # Assign to the correct broken values
        power_array[i] = 1 - cdf_pos + cdf_neg

    return sub_array, power_array

