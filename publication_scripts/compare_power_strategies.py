
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
    draw_distribution_amplitude,
    draw_true_effects,
    draw_subject_array,
    group_level_effect,
    stack_subject_arrays
)


# Set seed for effect model and draw true effects
# Only one set of true effects is fine for now
SEED = 20260724
rng_np = np.random.default_rng(SEED)
N_NODES = 55
N_VARIABLES = N_NODES*(N_NODES - 1)//2  # Not really a constant but fine
TAU_A = 1.0
TAU_S = 1.0
C = 0.9
C_DRAW = 0.9

# Sample size - 40 subjects - idea scale
SAMPLE_SIZE = 40

# For K values 10, 20, 50, 100, 200 - number of winners curse predictors
K_VALUES = (10, 20, 50, 100, 200)
K_DATASET = (400, 800)


def compare_power_strats(
):

    # Estimator strategy lists
    ESTIMATORS = (
        estimate_power_strongest_effect,
        estimate_power_smallest_significant_effect,
        estimate_power_average_effect,
    )

    # Draw true effects
    A_edge = draw_distribution_amplitude(
        n_nodes=N_NODES,
        tau_A=TAU_A,
        rng_np=rng_np
    )

    TE = draw_true_effects(A_edge, C, rng_np=rng_np)


    def draw():
        return draw_subject_array(
            TE=TE,
            n_subs=SAMPLE_SIZE,
            tau_S=TAU_S,
            c=C_DRAW,
            rng_np=rng_np
        )


    # Create np array with columns (n3 vs n K values)
    results = np.zeros((len(ESTIMATORS), len(K_VALUES)))

    # Create stack of experiments
    stack_full = np.stack([draw() for _ in range(max(K_VALUES))])


    for k_idx, K in enumerate(K_VALUES):

        # Get K estimations from the full stack
        exp_heatmaps = group_level_effect(stack_full[:K], axis=1)

        # Compute power estimation for each study type and store in array
        # With the exception of subsampling repetition
        for e_idx, estimator in enumerate(ESTIMATORS):
            results[e_idx, k_idx] = estimator(
                exp_heatmaps, N_VARIABLES, SAMPLE_SIZE
            )

    # On subsampling repetion - draw more Ks - diff subjs more combinations
    power_subsample_rep = estimate_power_subsampling_repetition(
        stack_subject_arrays(stack_full)[:K_DATASET[0]],
        SAMPLE_SIZE
    )


    # Calculate true power using real effects
    true_power = estimate_true_power(
        TE,
        N_VARIABLES,
        SAMPLE_SIZE
    )
