
import numpy as np
import matplotlib.pyplot as plt

from power_estimation_modes.study_planning_strats import (
    estimate_power_strongest_effect,
    estimate_power_smallest_significant_effect,
    estimate_power_average_effect,
    estimate_power_subsampling_repetition,
    estimate_true_power
)

from power_estimation_modes.effect_model import (
    draw_true_effects,
    draw_subject_array,
    group_level_effect,
    stack_subject_arrays
)


def generate_estimator_comp_figure(
        estimator,
        n_variables,
        tau_A,
        tau_S,
        tau_M,
        k_values,
        sample_sizes,
        seed=None
):

    # Create np array with columns (n3 vs n K values)
    results = np.zeros((len(sample_sizes), len(k_values)))

    for i_s, n_sample in enumerate(sample_sizes):

        if seed is not None:
            rng_np = np.random.default_rng(seed)
        else:
            rng_np = np.random.default_rng()

        # Draw true effects
        TE = draw_true_effects(
            n_variables=n_variables,
            tau_A=tau_A,
            rng_np=rng_np
        )

        def draw():
            return draw_subject_array(
                TE=TE,
                n_subs=n_sample,
                tau_S=tau_S,
                tau_mu=tau_M,
                rng_np=rng_np
            )

        # Create stack of experiments
        stack_full = np.stack([draw() for _ in range(max(k_values))])

        # A little redundant but we aggregate everything here
        pooled_subjects = stack_subject_arrays(stack_full)  

        for k_idx, K in enumerate(k_values):

            # Get K estimations from the full stack
            exp_heatmaps = group_level_effect(stack_full[:K], axis=1)

            # Compute power estimation
            results[len(ESTIMATORS), k_idx] = estimate_power_subsampling_repetition(
                pooled_subjects[:K * SAMPLE_SIZE],
                N_VARIABLES,
                SAMPLE_SIZE,
                K,
                rng_np=rng_np
            )

        pass


