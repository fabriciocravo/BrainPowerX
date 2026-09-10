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
    calculate_power_fwer_normal
)
import numpy as np


def group_p_est_strongest_effect(
        group_effect_array,
        n_variables,
        sample_size,
):

    # Find maximum effect accross the group effect array
    max_effect = np.abs(group_effect_array).max()

    # Calculate power of that maximum effect
    power = calculate_power_fwer_normal(
        max_effect,
        n_variables,
        sample_size
    )

    return power
