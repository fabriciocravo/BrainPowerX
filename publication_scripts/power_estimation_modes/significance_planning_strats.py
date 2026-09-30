import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from effect_model import (
    draw_t_array_group_level
)
from utils import (
    pvalues_from_t,
    significance_map,
    calculate_power_fwer,
    calculate_t_power_fwer
)


# Faster and draws directly from grup distributions
# Since it's used for multiple repeated draws, it takes no seed
def get_exp_t_array(
        TE,
        n_subs
):
    
    return draw_t_array_group_level(
        TE=TE,
        n_subs=n_subs,
        tau_mu=0
    )


def first_significant_experiment(
        TE,
        n_variables,
        sample_size,
        alpha,
        max_sig_iteration
):

    i_b = 0
    while i_b < max_sig_iteration:
        i_b += 1

        # Draw true effects from TE model
        t_array = get_exp_t_array(
            TE=TE,
            n_subs=sample_size
        )

        r = significance_map(
            pvalues_from_t(t_array, sample_size),
            n_variables,
            alpha=alpha
        )

        if r.any():
            return t_array, r
 
    # Just return something with None - there will be some error here
    # if max_sig_iteration is low enough
    return t_array, None


# Power of strongest effect sizes with only sig studies
def p_sig_strongest_effect(
    TE,
    n_variables,
    sample_size,
    alpha,
    max_sig_iteration=10000
):

    t_sig_array, _ = first_significant_experiment(
        TE,
        n_variables,
        sample_size,
        alpha,
        max_sig_iteration
    )

    t_max = np.max(t_sig_array)
    te_max = np.max()

    # Calculate power based on the average significant effect
    power = calculate_t_power_fwer(
        t_max,
        n_variables,
        sample_size
    )

    true_power = calculate_power_fwer(
        te_max,
        n_variables,
        sample_size
    )

    return power, true_power


# The power for the significant effect is a little different
# Since only significant effects count:
# True power and emperical power must be computed at the same time
def p_sig_average_significant_effect(
        TE,
        n_variables,
        sample_size,
        alpha,
        max_sig_iteration=10000
):

    avg_sig = []
    te_sig = []

    t_sig_array, r = first_significant_experiment(
        TE,
        n_variables,
        sample_size,
        alpha,
        max_sig_iteration
    )

    # For each draw, find the average significant effect
    if r.any():
        avg_sig = np.abs(t_sig_array[r]).mean()
        te_sig = np.abs(TE[r]).mean()
    else:
        Warning('Consider raising max_sig_iteration')
        power = 0
        true_power = 0
        return power, true_power
    
    # Calculate power based on the average significant effect
    power = calculate_t_power_fwer(
        avg_sig,
        n_variables,
        sample_size
    )

    true_power = calculate_power_fwer(
        te_sig,
        n_variables,
        sample_size
    )

    return power, true_power

