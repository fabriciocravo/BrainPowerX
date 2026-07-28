import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from .effect_model import  group_level_effect

from .utils import (
    edges_to_pvalues,
    significance_map,
    calculate_power_fwer,
    upper
)


def estimate_power_strongest_effect(
        stack_heatmap,
        n_variables,
        sample_size
):

    # Find maximum effect accross all the stacked heatmaps
    max_effect = stack_heatmap.max()

    # Calculate power of that maximum effect
    return calculate_power_fwer(
        max_effect,
        n_variables,
        sample_size
    )


def estimate_power_smallest_significant_effect(
        stack_heatmap,
        n_variables,
        sample_size
):

    min_sig = []
    for E in stack_heatmap:
        e_up = upper(E)

        # Across each heatmap find all significant effects
        r = significance_map(edges_to_pvalues(e_up, sample_size))

        # For each heatmap find the minimum significant effect
        if r.any():
            min_sig.append(e_up[r].min())

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
        n_varibles=n_variables,
        N=sample_size
    )


def estimate_power_average_effect(
        stack_heatmap,
        n_variables,
        sample_size
):

    # For each heatmap - calculate average power
    avg_power = np.array([
        calculate_power_fwer(upper(E), n_variables, sample_size).mean()
        for E in stack_heatmap
    ])

    # Over K draws find the maximum average power
    return avg_power.max()


def estimate_power_subsampling_repetition(
    stacked_subject_array,
    sample_size,
    n_rep=500,
    rng_np=None
):

    if rng_np is None:
        rng_np = np.random.default_rng()

    # Get total dataset size
    data_set_size = stacked_subject_array.shape[0]

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
        sig = significance_map(edges_to_pvalues(gl_exp, sample_size))
        p_matrix += sig

    # Calculate proportion of detection per edges
    p_matrix = p_matrix/n_rep

    # Average results for average power and return
    avg_power = np.mean(upper(p_matrix))
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

    true_power = np.mean(upper(true_power))
    return true_power


if __name__ == '__main__':

    print(calculate_power_fwer(2, 40, 100))
