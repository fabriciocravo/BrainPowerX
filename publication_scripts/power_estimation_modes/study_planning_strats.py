import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from effect_model import (
    group_level_effect,
    stack_subject_arrays
)

from utils import (
    edges_to_pvalues,
    significance_map,
    calculate_power_fwer
)


def stack_eff(stacked_subject_array, exp_number):
    return stacked_subject_array[:exp_number]


def p_est_strongest_effect(
        stacked_subject_array,
        n_variables,
        sample_size,
        exp_number
):

    stacked_effects = stack_eff(stacked_subject_array, exp_number)

    # Find maximum effect accross all the stacked heatmaps
    avg_effects = group_level_effect(stacked_effects, axis=1)
    max_effect = np.abs(avg_effects).max()

    # Calculate power of that maximum effect
    power = calculate_power_fwer(
        max_effect,
        n_variables,
        sample_size
    )

    return power


def tp_strongest_effect(
        TE,
        n_variables,
        sample_size
):
    # Getting max true effect
    max_effect = TE.max()
    # Calculate power of that maximum effect
    power = calculate_power_fwer(
        max_effect,
        n_variables,
        sample_size
    )
    return power


def p_est_smallest_significant_effect(
        stacked_subject_array,
        n_variables,
        sample_size,
        exp_number
):

    stacked_effects = stack_eff(stacked_subject_array, exp_number)

    min_sig = []
    for e in stacked_effects:
        # Across each heatmap find all significant effects
        r = significance_map(edges_to_pvalues(e, sample_size), n_variables)

        # For each heatmap find the minimum significant effect
        if r.any():
            avg_e = group_level_effect(e, axis=0)
            min_sig.append(avg_e[r].min())

    if not min_sig:
        raise ValueError(
            'The power estimation using max '
            'significant effect did not return anything'
        )

    # Over K draws find the maximum minimum significant effect
    worst_min_sig = np.max(min_sig)

    # Calculate power based on the maximum minimum signifcant effect
    return calculate_power_fwer(
        e_mat=worst_min_sig,
        n_variables=n_variables,
        N=sample_size
    )


def p_est_average_significant_effect(
        stacked_subject_array,
        n_variables,
        sample_size,
        exp_number
):

    stacked_effects = stack_eff(stacked_subject_array, exp_number)

    avg_sig = []
    for e in stacked_effects:
        # Across each draw find all significant effects
        r = significance_map(edges_to_pvalues(e, sample_size), n_variables)

        # For each draw, find the average significant effect
        if r.any():
            avg_e = group_level_effect(e, axis=0)
            avg_sig.append(np.abs(avg_e[r]).mean())

    if not avg_sig:
        # Define power of non significance as zero
        return 0

    # Over K draws, get the maximum over the means.
    mean_sig = np.max(avg_sig)

    # Calculate power based on the average significant effect
    power = calculate_power_fwer(
        mean_sig,
        n_variables,
        sample_size
    )

    return power


def tp_average_significant_effect(
        TE,
        n_variables,
        sample_size
):
    pass


def p_est_average_effect(
        stacked_subject_array,
        n_variables,
        sample_size,
        exp_number
):

    stacked_effects = stack_eff(stacked_subject_array, exp_number)

    # For each heatmap - calculate average power
    all_means = []
    for e in stacked_effects:
        e = group_level_effect(e, axis=0)
        mean = np.abs(e).mean()
        all_means.append(mean)

    # Over K draws find the maximum absolute effect
    max_mean = np.asarray(all_means).max()

    power = calculate_power_fwer(
        max_mean,
        n_variables,
        sample_size
    )
    return power


def p_est_subsampling_repetition(
    stacked_subject_array,
    n_variables,
    sample_size,
    exp_number,
    n_rep=100,
    return_full_matrix=False,
    rng_np=None
):

    if rng_np is None:
        rng_np = np.random.default_rng()

    pooled_subjects = stack_subject_arrays(stacked_subject_array[:exp_number])

    # Get total dataset size
    data_set_size = pooled_subjects.shape[0]

    # Start empty counting matrix
    p_matrix = np.zeros_like(stacked_subject_array[0])

    # Each map is a subsampled experiment
    # For each n_rep chose a map at random
    for _ in range(n_rep):
  
        exp = pooled_subjects[
            rng_np.integers(data_set_size, size=sample_size)
        ]

        # Detect which edges are significant
        sig = significance_map(edges_to_pvalues(
            exp,
            sample_size),
            n_variables
        )

        p_matrix += sig

    # Calculate proportion of detection per edges
    p_matrix = p_matrix/n_rep

    # Average results for average power and return
    if not return_full_matrix:
        avg_power = np.mean(p_matrix)
        return avg_power
    else:
        return p_matrix


def estimate_true_power(
    true_effects,
    n_variables,
    sample_size,
    return_full_matrix=False
):

    true_power = calculate_power_fwer(
        true_effects,
        n_variables,
        sample_size
    )

    if not return_full_matrix:
        true_power = np.mean(true_power)
        return true_power
    else:
        return true_power


if __name__ == '__main__':

    print(calculate_power_fwer(2, 40, 100))
