import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from effect_model import (
    draw_t_array_sub_level,
    draw_t_array_group_level
)
from utils import (
    pvalues_from_t,
    p_values_true_effects,
    significance_map,
    calculate_power_fwer,
    calculate_t_power_fwer
)


# Slower and more accurate
def get_total_t_array(
        seed_array,
        TE,
        n_subs,
        tau_mu,
        exp_number,
):

    def draw(i):
        return draw_t_array_sub_level(
            seed_list=seed_array[i],
            TE=TE,
            n_subs=n_subs,
            tau_mu=tau_mu,
        )

    total_effect_array = [draw(i) for i in range(exp_number)]

    return total_effect_array


def p_est_strongest_effect(
        seed_array,
        TE,
        n_variables,
        sample_size,
        tau_M,
        exp_number
):

    total_t_array = get_total_t_array(
        seed_array=seed_array,
        TE=TE,
        n_subs=sample_size,
        tau_mu=tau_M,
        exp_number=exp_number
    )

    max_effect = np.abs(total_t_array).max()

    # Calculate power of that maximum t-stat
    power = calculate_t_power_fwer(
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
    max_effect = np.abs(TE).max()

    # Calculate power of that maximum effect
    power = calculate_power_fwer(
        max_effect,
        n_variables,
        sample_size
    )

    return power


def p_est_effect_number(
        seed_array,
        TE,
        n_variables,
        sample_size,
        tau_M,
        exp_number,
        effect_number=100,
):
    
    total_t_array = get_total_t_array(
        seed_array=seed_array,
        TE=TE,
        n_subs=sample_size,
        tau_mu=tau_M,
        exp_number=exp_number
    )

    top_effect_array = np.sort(np.abs(total_t_array))[-effect_number:]

    # Calculate power of that maximum t-stat
    power = calculate_t_power_fwer(
        top_effect_array,
        n_variables,
        sample_size
    )

    return power


def tp_effect_number(
        TE,
        n_variables,
        sample_size,
        effect_number,
):
    # Getting max true effect
    top_eff = np.sort(np.abs(TE))[-effect_number:]

    # Calculate power of that maximum effect
    power = calculate_power_fwer(
        top_eff,
        n_variables,
        sample_size
    )

    return power


def p_est_subsampling_repetition(
    seed_array,
    TE,
    n_variables,
    sample_size,
    tau_M,
    exp_number,
    n_rep=100,
    return_full_matrix=False,
    rng_np=None
):

    if tau_M != 0:
        raise ValueError("This function does not support tau_M != 0")

    if rng_np is None:
        rng_np = np.random.default_rng()

    # unpack all seeds - all subjects are used here
    pooled_seeds = np.concatenate(
        seed_array[:exp_number],
        axis=0
    )

    # pool the subjects
    chosen_seeds = pooled_seeds[
        rng_np.integers(pooled_seeds.shape[0], size=sample_size)
    ]

    # Start empty counting matrix
    p_matrix = np.zeros(n_variables, dtype=float)

    # Each map is a subsampled experiment
    # For each n_rep chose a map at random
    for _ in range(n_rep):
  
        chosen_seeds = pooled_seeds[
            rng_np.integers(
                pooled_seeds.shape[0],
                size=sample_size
            )
        ]

        t_exp = draw_t_array_sub_level(
            seed_list=chosen_seeds,
            TE=TE,
            n_subs=sample_size,
            tau_mu=0
        )

        # Detect which edges are significant
        sig = significance_map(pvalues_from_t(
            t_exp,
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
