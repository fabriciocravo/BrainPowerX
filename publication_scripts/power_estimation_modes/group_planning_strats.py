from effect_model import (
    group_level_effect
)
from utils import (
    edges_to_pvalues,
    p_values_true_effects,
    significance_map,
    calculate_power_fwer
)
from utils import(
    calculate_power_fwer
)
import numpy as np


def group_p_est_strongest_effect(
        group_effect_array,
        group_variance_array,
        n_variables,
        sample_size,
):

    # Find maximum effect accross the group effect array
    effect_est = group_effect_array/np.sqrt(group_variance_array)
    max_effect = np.abs(effect_est).max()

    # Calculate power of that maximum effect
    power = calculate_power_fwer(
        max_effect,
        n_variables,
        sample_size
    )

    return power


def group_tp_strongest_effect(
        group_effect_array,
        n_variables,
        sample_size,
):

    # Find maximum effect accross the group effect array
    max_effect = np.abs(group_effect_array).max()

    # Calculate power of that maximum effect
    power = calculate_power_fwer(
        max_effect,
        n_variables,
        sample_size
    )

    return power


def group_p_est_average_significant_effect(
        group_effect_array,
        group_variance_array,
        n_variables,
        sample_size,
):

    raise TypeError('Function not yet completed')

    # Across each draw find all significant effects
    r = significance_map(
        edges_to_pvalues(group_effect_array, sample_size),
        n_variables
    )

    # For each draw, find the average significant effect
    if r.any():
        avg_e = group_level_effect(group_effect_array, axis=0)
        avg_sig = np.abs(avg_e[r]).mean()

    if not avg_sig:
        # Define power of non significance as zero
        return 0

    # Calculate power based on the average significant effect
    power = calculate_power_fwer(
        avg_sig,
        n_variables,
        sample_size
    )

    return power
