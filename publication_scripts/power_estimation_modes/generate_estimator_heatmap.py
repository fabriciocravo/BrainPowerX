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
    draw_subject_array,
)
from joblib import Parallel, delayed


def generate_estimator_comp_figure(
        estimator,
        true_power_estimator,
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
    true_power = np.zeros(len(sample_sizes))

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

    for i_s, n_sample in enumerate(sample_sizes):

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

        # Create stack of experiments
        stack_full = np.stack([draw() for _ in range(max(k_values))])

        for k_idx, K in enumerate(k_values):

            results[i_s, k_idx] = estimator(
                stack_full,
                n_variables,
                n_sample,
                K
            )

    results_diff = np.abs(results - true_power[:, None])

    print(seed)

    return results, results_diff


def plot_curve_and_heatmap(
    results_mean,
    diff_mean,
    ci_lower,
    ci_upper,
    sample_sizes,
    k_values,
    k_curve,
    figsize=(12, 5),
):
    # Create figure and subplots
    # The K per error curve to left and heatmap to right
    fig, (ax_curve, ax_heat) = plt.subplots(1, 2, figsize=figsize)

    # Get the index of subjects for the curve
    n_idx = list(k_values).index(k_curve)

    mean_vals = results_mean[:, n_idx]
    yerr_lower = np.clip(mean_vals - ci_lower[:, n_idx], 0, 1)
    yerr_upper = np.clip(ci_upper[:, n_idx] - mean_vals, 0, 1)

    # Plot K versus error curve for select sample size
    ax_curve.errorbar(
        sample_sizes,
        mean_vals,
        yerr=[yerr_lower, yerr_upper],
        marker="o",
        capsize=4,
        label="Estimated power"
    )
    ax_curve.set_xlabel("Number of Subjects")
    ax_curve.set_ylabel("Estimated power")
    ax_curve.set_ylim(0, 1)
    ax_curve.set_title(f"Power estimation with K studies={k_curve}")

    true_power = results_mean - diff_mean

    ax_curve.axhline(
        true_power[n_idx, 0],
        linestyle="--",
        color="k",
        label="True power"
    )
    ax_curve.legend()

    vmax = np.max(np.abs(diff_mean))

    im = ax_heat.imshow(
        diff_mean,
        cmap="RdBu_r",
        vmin=-vmax,
        vmax=vmax,
        interpolation="nearest",
        aspect="auto",
    )

    n_rows, n_cols = diff_mean.shape

    ax_heat.set_xticks(range(len(k_values)))
    ax_heat.set_xticklabels(k_values)
    ax_heat.set_yticks(range(len(sample_sizes)))
    ax_heat.set_yticklabels(sample_sizes)
    ax_heat.set_xlabel("K")
    ax_heat.set_ylabel("N")
    ax_heat.set_title("Estimated − True power")

    for i in range(n_rows):
        for j in range(n_cols):
            ax_heat.text(
                j,
                i,
                f"{diff_mean[i, j]:.2f}",
                ha="center",
                va="center",
                fontsize=8,
            )

    plt.colorbar(im, ax=ax_heat, label="Estimated − True power")

    fig.tight_layout()

    return fig, (ax_curve, ax_heat)


if __name__ == "__main__":

    ESTIMATOR = p_est_strongest_effect
    # ESTIMATOR = p_est_average_significant_effect
    # ESTIMATOR = p_est_subsampling_repetition

    # - Recalculate this
    SEED = 20260724
    N_NODES = 268
    N_VARIABLES = N_NODES * (N_NODES - 1) // 2
    TAU_A = 0.00088
    TAU_S = 1.0
    TAU_MU = 0

    N_REPS = 10
    SAMPLE_SIZES = [10, 20, 40, 80, 120]
    K_VALUES = (1, 5, 10, 20, 40, 100)

    ESTIMATOR_TO_TRUE_POWER = {
        p_est_strongest_effect: tp_strongest_effect,
        p_est_average_significant_effect: tp_average_significant_effect,
        p_est_average_effect: estimate_true_power,
        p_est_subsampling_repetition: estimate_true_power,
    }
    ESTIMATOR_TP = ESTIMATOR_TO_TRUE_POWER[ESTIMATOR]

    results_sum = np.zeros((len(SAMPLE_SIZES), len(K_VALUES)))
    results_sq_sum = np.zeros((len(SAMPLE_SIZES), len(K_VALUES)))
    diff_sum = np.zeros((len(SAMPLE_SIZES), len(K_VALUES)))

    # Main loop - estimate power difference with LLN
    results_list = Parallel(n_jobs=1)(
        delayed(generate_estimator_comp_figure)(
            estimator=ESTIMATOR,
            true_power_estimator=ESTIMATOR_TP,
            n_variables=N_VARIABLES,
            tau_A=TAU_A,
            tau_S=TAU_S,
            tau_M=TAU_MU,
            k_values=K_VALUES,
            sample_sizes=SAMPLE_SIZES,
            seed=i,
        )
        for i in range(N_REPS)
    )

    for results, results_diff in results_list:
        results_sum += results
        results_sq_sum += results ** 2
        diff_sum += results_diff

    results_mean = results_sum / N_REPS
    variance = (results_sq_sum / N_REPS) - results_mean ** 2
    std = np.sqrt(variance)
    std = np.sqrt(variance)
    sem = std / np.sqrt(N_REPS)
    ci_lower = results_mean - 1.96 * sem
    ci_upper = results_mean + 1.96 * sem

    diff_mean = diff_sum / N_REPS

    fig, _ = plot_curve_and_heatmap(
        results_mean,
        diff_mean,
        ci_lower,
        ci_upper,
        SAMPLE_SIZES,
        K_VALUES,
        k_curve=40,
    )
    plt.show()
