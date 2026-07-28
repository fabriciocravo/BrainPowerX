import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from .effect_model import (
    group_level_effect,
    stack_subject_arrays
) 

from .utils import (
    edges_to_pvalues,
    significance_map,
    calculate_power_fwer
)


def stack_eff(stacked_subject_array, exp_number):

    stacked_effects = group_level_effect(
        stacked_subject_array[:exp_number],
        axis=1
    )

    return stacked_effects


def estimate_power_strongest_effect(
        stacked_subject_array,
        n_variables,
        sample_size,
        exp_number
):

    stacked_effects = stack_eff(stacked_subject_array, exp_number)

    # Find maximum effect accross all the stacked heatmaps
    max_effect = stacked_effects.max()

    # Calculate power of that maximum effect
    return calculate_power_fwer(
        max_effect,
        n_variables,
        sample_size
    )


def estimate_power_smallest_significant_effect(
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
            min_sig.append(e[r].min())

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


def estimate_power_average_significant_effect(
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
            avg_sig.append(e[r].mean())

    if not avg_sig:
        raise ValueError(
            'The power estimation using average '
            'significant effect did not return anything'
        )

    # Over K draws, average the per-draw average significant effect
    mean_sig = np.mean(avg_sig)

    # Calculate power based on the average significant effect
    return calculate_power_fwer(
        mean_sig,
        n_variables,
        sample_size
    )


def estimate_power_average_effect(
        stacked_subject_array,
        n_variables,
        sample_size,
        exp_number
):

    stacked_effects = stack_eff(stacked_subject_array, exp_number)

    # For each heatmap - calculate average power
    avg_power = np.array([
        calculate_power_fwer(e, n_variables, sample_size).mean()
        for e in stacked_effects
    ])

    # Over K draws find the maximum average power
    return avg_power.max()


def estimate_power_subsampling_repetition(
    stacked_subject_array,
    n_variables,
    sample_size,
    exp_number,
    n_rep=500,
    rng_np=None
):

    if rng_np is None:
        rng_np = np.random.default_rng()

    pooled_subjects = stack_subject_arrays(stacked_subject_array)

    print(pooled_subjects.shape)
    exit()

    # Get total dataset size
    data_set_size = pooled_subjects.shape[0]
    if int(sample_size*exp_number) != data_set_size:
        raise ValueError('Error received an incorrect number of samples')

    # Start empty counting matrix
    p_matrix = np.zeros_like(stacked_subject_array[0])

    # Each map is a subsampled experiment
    # For each n_rep chose a map at random
    for _ in range(n_rep):

        exp = stacked_subject_array[
            rng_np.integers(data_set_size, size=sample_size)
        ]

        gl_exp = group_level_effect(exp)

        # Detect which edges are significant
        sig = significance_map(edges_to_pvalues(
            gl_exp,
            sample_size),
            n_variables
        )

        p_matrix += sig

    # Calculate proportion of detection per edges
    p_matrix = p_matrix/n_rep

    # Average results for average power and return
    avg_power = np.mean(p_matrix)
    return avg_power


def estimate_true_power(
    true_effects,
    n_variables,
    sample_size
):

    true_power = calculate_power_fwer(
        true_effects,
        n_variables,
        sample_size
    )

    true_power = np.mean(true_power)
    return true_power


if __name__ == '__main__':

    print(calculate_power_fwer(2, 40, 100))
