import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from true_effect_models import (
    normal_true_effects
)
from significance_planning_strats import (
    p_sig_strongest_effect,
    p_sig_average_significant_effect
)
from joblib import(
    Parallel,
    delayed
)


# Script Parameters ###########################
N_NODES = 268
N_VARIABLES = N_NODES * (N_NODES - 1) // 2

# Normal model ###########################
TAU_A = 0.00088
TAU_S = 1.0
TAU_MU = 0


def TE_normal(n_var, rng):
    return normal_true_effects(
        n_variables=n_var,
        tau_A=TAU_A,
        tau_S=TAU_S,
        rng_np=rng
    )


######################################
N_REPS = 1000
SAMPLE_SIZES = [10, 20, 40, 80, 120]
ALPHA_VALUES = (0.10, 0.05, 0.01, 0.001)


def significance_heamap_cuve(
        TE_model,
        estimator,
        n_variables,
        sample_sizes,
        alpha_v_list,
        max_sig_iteration=10000,
        seed=None
):

    # Create np array with columns (n3 vs n K values)
    results = np.zeros((len(sample_sizes), len(alpha_v_list)))
    true_power = np.zeros((len(sample_sizes), len(alpha_v_list)))

    if seed is not None:
        rng_np = np.random.default_rng(seed)
    else:
        rng_np = np.random.default_rng()

    # Draw true effects
    TE = TE_model(n_variables, rng_np)

    for i_s, n_sample in enumerate(sample_sizes):
        for a_idx, alpha in enumerate(alpha_v_list):

            results[i_s, a_idx], true_power[i_s, a_idx] = \
                estimator(
                    TE,
                    n_variables=n_variables,
                    sample_size=n_sample,
                    alpha=alpha,
                    max_sig_iteration=max_sig_iteration
                )

    results_diff = np.abs(results - true_power)

    print(seed)

    return results, results_diff, true_power


def plot_curve_and_heatmap(
    results_mean,
    diff_mean,
    true_power,
    ci_lower,
    ci_upper,
    sample_sizes,
    alpha_values,
    n_curve,
    figsize=(12, 5),
):
    
    # Create figure and subplots
    # The K per error curve to left and heatmap to right
    fig, (ax_curve, ax_heat) = plt.subplots(1, 2, figsize=figsize)

    # Get the index of subjects for the curve
    n_idx = list(sample_sizes).index(n_curve)

    mean_vals = results_mean[n_idx, :]
    yerr_lower = np.clip(mean_vals - ci_lower[n_idx, :], 0, 1)
    yerr_upper = np.clip(ci_upper[n_idx, :] - mean_vals, 0, 1)

    ax_curve.errorbar(
        alpha_values,
        mean_vals,
        yerr=[yerr_lower, yerr_upper],
        marker="o",
        capsize=4,
        label="Estimated power"
    )
    ax_curve.set_xlabel(r"Significance Alpha $\alpha$")
    ax_curve.invert_xaxis()
    ax_curve.set_ylabel("Estimated power")
    ax_curve.set_ylim(0, 1)
    ax_curve.set_title(f"Power estimation at N={n_curve}")

    ax_curve.plot(
        alpha_values,
        true_power[n_idx, :],
        linestyle="--",
        marker="s",
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

    ax_heat.set_xticks(range(len(alpha_values)))
    ax_heat.set_xticklabels(alpha_values)
    ax_heat.set_yticks(range(len(sample_sizes)))
    ax_heat.set_yticklabels(sample_sizes)
    ax_heat.set_xlabel(r"$\alpha$")
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


def sigficance_power_error_vs_sample_size(
        TE_model,
        estimator,
        n_variables,
        sample_sizes,
        max_sig_iteration=10000,
        seed=None
):
    
    # Model the error in the power estimation versus the sample size
    if seed is not None:
        rng_np = np.random.default_rng(seed)
    else:
        rng_np = np.random.default_rng()

    # Draw true effects
    TE = TE_model(n_variables, rng_np)

    power_error = np.zeros((len(sample_sizes)))
    true_power = np.zeros((len(sample_sizes)))
    results = np.zeros((len(sample_sizes)))

    for i_s, n_sample in enumerate(sample_sizes):

        results[i_s], true_power[i_s] = \
            estimator(
                TE,
                n_variables=n_variables,
                sample_size=n_sample,
                alpha=0.05,
                max_sig_iteration=max_sig_iteration
            )

        power_error[i_s] = np.abs(true_power[i_s] - results[i_s])

    return power_error


def gen_heat_map(TE_model, estimator):

    results_sum = np.zeros((len(SAMPLE_SIZES), len(ALPHA_VALUES)))
    results_sq_sum = np.zeros((len(SAMPLE_SIZES), len(ALPHA_VALUES)))
    diff_sum = np.zeros((len(SAMPLE_SIZES), len(ALPHA_VALUES)))

    # Main loop - estimate power difference with LLN
    results_list = Parallel(n_jobs=10)(
        delayed(significance_heamap_cuve)(
            TE_model=TE_model,
            estimator=estimator,
            n_variables=N_VARIABLES,
            alpha_v_list=ALPHA_VALUES,
            sample_sizes=SAMPLE_SIZES,
            seed=i,
        )
        for i in range(N_REPS)
    )

    true_power_sum = np.zeros((len(SAMPLE_SIZES), len(ALPHA_VALUES)))
    for results, results_diff, tp in results_list:
        results_sum += results
        results_sq_sum += results ** 2
        diff_sum += np.abs(results_diff)
        true_power_sum += tp

    true_power_mean = true_power_sum / N_REPS
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
        true_power_mean,
        ci_lower,
        ci_upper,
        SAMPLE_SIZES,
        ALPHA_VALUES,
        n_curve=40,
    )
    plt.show()


def gen_sample_size_curve(TE_model, estimator):

    # Sample size curve parameters
    N_NODES = 268
    N_VARIABLES = N_NODES * (N_NODES - 1) // 2
    TAU_A = 0.00088
    TAU_S = 1.0

    N_REPS = 500
    SAMPLE_SIZES = [10, 20, 40, 80]

    subsample_lists = Parallel(
        n_jobs=5, backend='loky')(
        delayed(sigficance_power_error_vs_sample_size)(
            n_variables=N_VARIABLES,
            tau_A=TAU_A,
            tau_S=TAU_S,
            tau_M=0,
            sample_sizes=SAMPLE_SIZES,
            seed=i
        ) for i in range(N_REPS)
    )

    # Aggregate across repetitions: shape (N_REPS, len(SAMPLE_SIZES))
    # -> mean/std per sample size
    power_error_array = np.stack(subsample_lists, axis=0)
    mean_error = power_error_array.mean(axis=0)
    std_error = power_error_array.std(axis=0)

    n_reps_actual = power_error_array.shape[0]
    sem = std_error / np.sqrt(n_reps_actual)
    ci95 = 1.96 * sem

    plt.errorbar(
        SAMPLE_SIZES,
        mean_error,
        yerr=ci95,
        marker='o',
        capsize=3
    )
    plt.xscale('log')
    plt.xlabel('Sample size')
    plt.ylabel('Power error (|true power - estimated power|)')
    plt.title('Power error vs. sample size')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    gen_heat_map(TE_normal, p_sig_average_significant_effect)
    pass
