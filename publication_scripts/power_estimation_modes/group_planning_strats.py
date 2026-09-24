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
        TE,
        n_variables,
        sample_size,
):

    # Find maximum effect accross the group effect array
    max_effect = np.abs(TE).max()

    # Calculate power of that maximum effect
    power = calculate_power_fwer(
        max_effect,
        n_variables,
        sample_size
    )

    return power


def group_p_effect_number(
        group_effect_array,
        group_variance_array,
        n_variables,
        sample_size,
        effect_number=100
):

    # Adjust effects according to new variance
    effect_est = group_effect_array/np.sqrt(group_variance_array)
    top_group_effects = np.sort(np.abs(effect_est))[-100:]
    
    # Calculate power based on the average significant effect
    power = calculate_power_fwer(
        top_group_effects,
        n_variables,
        sample_size
    )

    return power


def group_tp_effect_number(
        TE,
        n_variables,
        sample_size,
        effect_number=100
):

    # Find maximum effect accross the group effect array
    top_effects = np.sorted(np.abs(TE))[-effect_number:]

    # Calculate power of that maximum effect
    power = calculate_power_fwer(
        top_effects,
        n_variables,
        sample_size
    )

    return power