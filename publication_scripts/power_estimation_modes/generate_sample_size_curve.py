import numpy as np
import matplotlib.pyplot as plt

from study_planning_strats import (
    p_est_strongest_effect,
    p_est_average_significant_effect,
    p_est_average_effect,
    p_est_subsampling_repetition,
    tp_strongest_effect,
    tp_average_significant_effect,
    estimate_true_power
)

from effect_model import (
    draw_true_effects,
    draw_subject_array
)


def generate_estimator_vs_n(
        estimator,
        true_power_estimator,
        n_variables,
        tau_A,
        tau_S,
        tau_M,
        K,
        sample_sizes,
        seed=None
):
    """
    Fixed K, varying N. Returns estimated power and true power
    as 1D arrays over sample_sizes.
    """

    results = np.zeros(len(sample_sizes))
    true_power = np.zeros(len(sample_sizes))

    for i_s, n_sample in enumerate(sample_sizes):

        if seed is not None:
            rng_np = np.random.default_rng(seed)
        else:
            rng_np = np.random.default_rng()

        # Draw true effects
        TE = draw_true_effects(
            n_variables=n_variables,
            tau_A=tau_A,
            tau_S=tau_S,
            rng_np=rng_np
        )

        # Deterministic given TE and n_sample -> compute once
        true_power[i_s] = true_power_estimator(
            TE,
            n_variables,
            n_sample
        )

        def draw():
            return draw_subject_array(
                TE=TE,
                n_subs=n_sample,
                tau_mu=tau_M,
                rng_np=rng_np
            )

        # Create stack of K experiments at this N
        stack_full = np.stack([draw() for _ in range(K)])

        results[i_s] = estimator(
            stack_full,
            n_variables,
            n_sample,
            K
        )

    return results, true_power


def plot_power_vs_n(
    sample_sizes,
    results_mean,
    true_power_mean,
    K,
    estimator_name="",
    figsize=(7, 5),
):
    fig, ax = plt.subplots(figsize=figsize)

    ax.plot(
        sample_sizes,
        results_mean,
        marker="o",
        label="Estimated power",
    )
    ax.plot(
        sample_sizes,
        true_power_mean,
        marker="o",
        linestyle="--",
        color="k",
        label="True power",
    )

    ax.set_xlabel("N (sample size)")
    ax.set_ylabel("Power")
    ax.set_ylim(0, 1)
    ax.set_title(f"{estimator_name} (K = {K})")
    ax.legend()

    fig.tight_layout()

    return fig, ax


if __name__ == "__main__":

    N_NODES = 30
    N_VARIABLES = N_NODES * (N_NODES - 1) // 2
    TAU_A = 0.00088
    TAU_S = 1.0
    TAU_MU = 0

    N_REPS = 10
    SAMPLE_SIZES = [10, 20, 40, 80, 120]
    K = 3

    ESTIMATOR = p_est_average_significant_effect

    ESTIMATOR_TO_TRUE_POWER = {
        p_est_strongest_effect: tp_strongest_effect,
        p_est_average_significant_effect: tp_average_significant_effect,
        p_est_average_effect: estimate_true_power,
        p_est_subsampling_repetition: estimate_true_power,
    }
    ESTIMATOR_TP = ESTIMATOR_TO_TRUE_POWER[ESTIMATOR]

    results_sum = np.zeros(len(SAMPLE_SIZES))
    true_power_sum = np.zeros(len(SAMPLE_SIZES))

    for i_rep in range(N_REPS):
        print(f'Percentage done: {i_rep/N_REPS}')

        results, true_power = generate_estimator_vs_n(
            estimator=ESTIMATOR,
            true_power_estimator=ESTIMATOR_TP,
            n_variables=N_VARIABLES,
            tau_A=TAU_A,
            tau_S=TAU_S,
            tau_M=TAU_MU,
            K=K,
            sample_sizes=SAMPLE_SIZES,
            seed=None,
        )
        results_sum += results
        true_power_sum += true_power

    results_mean = results_sum / N_REPS
    true_power_mean = true_power_sum / N_REPS

    fig, _ = plot_power_vs_n(
        SAMPLE_SIZES,
        results_mean,
        true_power_mean,
        K,
        estimator_name=ESTIMATOR.__name__,
    )

    plt.show()
