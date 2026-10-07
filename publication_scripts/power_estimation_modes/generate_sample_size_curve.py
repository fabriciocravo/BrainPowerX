import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

from utils import (
    calculate_power_fwer,
    calculate_t_power_fwer
)
from effect_model import (
    draw_t_array_group_level
)
from true_effect_models import (
    normal_true_effects
)


def generate_estimator_vs_n(
        TE_model,
        n_effect_est,
        n_variables,
        sample_sizes,
        seed=None
):

    if n_effect_est == 0 or n_effect_est > n_variables:
        raise ValueError(
            'n_est_effects either zero or greater than var number'
        )

    results = np.zeros(len(sample_sizes))
    true_power_arr = np.zeros(len(sample_sizes))

    for i_s, n_sample in enumerate(sample_sizes):

        if seed is not None:
            rng_np = np.random.default_rng(seed)
        else:
            rng_np = np.random.default_rng()

        # Draw true effects
        TE = TE_model(n_variables, rng_np)
        qTE = np.sort(TE)[-n_effect_est:]

        # Deterministic given TE and n_sample -> compute once
        true_power = calculate_power_fwer(
            qTE,
            n_variables,
            n_sample
        )
        true_power = true_power.mean()
        true_power_arr[i_s] = true_power

        t_array = draw_t_array_group_level(
            TE=TE,
            n_subs=n_sample,
            tau_mu=0
        )
        qT = np.sort(t_array)[-n_effect_est:]

        estimated_p = calculate_t_power_fwer(
            qT,
            n_variables,
            n_sample,
        )

        results[i_s] = np.abs(estimated_p - true_power)

    return results, true_power_arr


def plot_power_vs_n(
    sample_sizes,
    results_mean,
    figsize=(7, 5),
):
    fig, ax = plt.subplots(figsize=figsize)

    ax.plot(
        sample_sizes,
        results_mean,
        marker="o",
        color="red",
        label="Power error",
    )

    ax.set_xlabel("N (sample size)")
    ax.set_ylabel("Power Error")
    ax.set_ylim(0, 1)
    ax.legend()

    fig.tight_layout()

    return fig, ax


if __name__ == "__main__":

    N_NODES = 30
    N_VARIABLES = N_NODES * (N_NODES - 1) // 2

    EFFECT_NUMBER_LIST = [
        1/N_VARIABLES
    ]

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

    N_REPS = 10
    N_JOBS = 10
    SAMPLE_SIZES = [10, 20, 40, 80, 120]

    size = (len(EFFECT_NUMBER_LIST), len(SAMPLE_SIZES))
    results_sum = np.zeros(size)

    for i_e, eff_n in enumerate(EFFECT_NUMBER_LIST):

        n_effect_est = max(1, int(round(eff_n * N_VARIABLES)))

        outputs = Parallel(n_jobs=N_JOBS, verbose=5)(
            delayed(generate_estimator_vs_n)(
                TE_model=TE_normal,
                n_effect_est=n_effect_est,
                n_variables=N_VARIABLES,
                sample_sizes=SAMPLE_SIZES,
                seed=None,
            )
            for _ in range(N_REPS)
        )

        for results, _true_power in outputs:
            results_sum[i_e, :] += results

    results_mean = results_sum / N_REPS

    fig, _ = plot_power_vs_n(
        SAMPLE_SIZES,
        results_mean[0],
    )

    plt.show()