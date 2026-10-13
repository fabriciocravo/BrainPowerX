import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from itertools import cycle, islice

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
        m_pilots,
        n_sample,
        seed=None
):
    """
    m_pilots: pilot sizes as multiples of n_sample
        (pilot size = round(m * n_sample), at least 2 subjects).
    """

    if n_effect_est == 0:
        raise ValueError('n_effect_est is zero')

    if n_effect_est > n_variables:
        n_effect_est = n_variables

    results = np.zeros(len(m_pilots))
    power_est = np.zeros(len(m_pilots))
    true_power_arr = np.zeros(len(m_pilots))

    rng_np = np.random.default_rng(seed)

    # Draw true effects
    TE = np.abs(TE_model(n_variables, rng_np))
    qTE = np.sort(TE)[-n_effect_est:]

    # Deterministic given TE and n_sample -> compute once
    true_power = calculate_power_fwer(
        qTE,
        n_variables,
        n_sample
    ).mean()

    for i_p, m_p in enumerate(m_pilots):

        # Pilot size in subjects, relative to the target sample size
        n_p = int(round(m_p * n_sample))

        t_array = draw_t_array_group_level(
            TE=TE,
            n_subs=n_p,
            tau_mu=0
        )
        t_array = np.abs(t_array)
        qT = np.sort(t_array)[-n_effect_est:]

        # Convert to t-stats for estimated sample size
        qT = qT * np.sqrt(n_sample / n_p)

        estimated_p = calculate_t_power_fwer(
            qT,
            n_variables,
            n_sample,
        ).mean()

        true_power_arr[i_p] = true_power
        power_est[i_p] = estimated_p
        results[i_p] = np.abs(estimated_p - true_power)

    return results, power_est, true_power_arr


def plot_quantile_comparisson(
    m_pilots,
    results_mean,
    n_effects_list,
    quantile_list,
    sample_sizes,
    tau_A,
    figsize=(7, 5),
):
    """
    results_mean: array of shape (n_quantiles, n_sample_sizes, n_pilot_sizes).
    One panel per sample size, all quantiles in each panel.
    """
    nss = len(sample_sizes)
    fig, ax = plt.subplots(1, nss, figsize=figsize)

    fig.suptitle(
        rf"Power planning for $\tau_A$ = {tau_A:g}"
    )

    for i_s in range(nss):

        ax[i_s].set_title(
            f"Sample size {sample_sizes[i_s]}",
            fontsize=14,
            fontweight="bold"
        )

        for i_q, q in enumerate(quantile_list):
            ax[i_s].plot(
                m_pilots,
                results_mean[i_q, i_s],
                marker="o",
                label=f"{q:.3g} ({n_effects_list[i_q]} effects)",
            )

        ax[i_s].set_xlabel(r"Pilot sample size ($n_{pilot}\,/\,n_{sample}$)")
        ax[i_s].set_ylabel("Power Error")
        ax[i_s].set_ylim(bottom=0)
        ax[i_s].legend(title="Quantile")

    fig.tight_layout()

    return fig, ax


if __name__ == "__main__":

    N_NODES = 268
    N_VARIABLES = N_NODES * (N_NODES - 1) // 2

    # Controllable parameters
    EFFECT_FRACTION_LIST = [
        0.01, 0.1, 0.3, 0.5, 1
    ]

    SAMPLE_SIZES = [40, 80, 120]
    M_PILOTS = [0.1, 0.25, 0.5, 1, 2, 5]

    TAU_A = 0.025
    TAU_S = 1.0
    TAU_MU = 0

    def TE_normal(n_var, rng):
        return normal_true_effects(
            n_variables=n_var,
            tau_A=TAU_A,
            tau_S=TAU_S,
            rng_np=rng
        )

    N_REPS = [20000, 10000, 5000, 5000, 5000]
    n_reps_list = list(islice(cycle(N_REPS), len(EFFECT_FRACTION_LIST)))
    N_JOBS = 10

    # Shape: (n_quantiles, n_sample_sizes, n_pilots)
    size = (len(EFFECT_FRACTION_LIST), len(SAMPLE_SIZES), len(M_PILOTS))
    results_mean = np.zeros(size)
    est_p_mean = np.zeros(size)
    tp_mean = np.zeros(size)

    # Number of effects per quantile (independent of sample size)
    n_effects_list = [
        max(1, int(round(eff_n * N_VARIABLES)))
        for eff_n in EFFECT_FRACTION_LIST
    ]

    for i_ns, n_sample in enumerate(SAMPLE_SIZES):

        for i_e, (n_effect_est, n_reps) in enumerate(
            zip(n_effects_list, n_reps_list)
        ):

            outputs = Parallel(n_jobs=N_JOBS, verbose=5)(
                delayed(generate_estimator_vs_n)(
                    TE_model=TE_normal,
                    n_effect_est=n_effect_est,
                    n_variables=N_VARIABLES,
                    m_pilots=M_PILOTS,
                    n_sample=n_sample,
                    seed=None,
                )
                for _ in range(n_reps)
            )

            for results, est_p, tp in outputs:
                results_mean[i_e, i_ns, :] += results
                est_p_mean[i_e, i_ns, :] += est_p
                tp_mean[i_e, i_ns, :] += tp

    n_reps_arr = np.array(n_reps_list)[:, None, None]
    results_mean = results_mean / n_reps_arr
    est_p_mean = est_p_mean / n_reps_arr
    tp_mean = tp_mean / n_reps_arr
    
    fig, _ = plot_quantile_comparisson(
        M_PILOTS,
        results_mean,
        n_effects_list,
        EFFECT_FRACTION_LIST,
        SAMPLE_SIZES,
        tau_A=TAU_A,
        figsize=(7 * len(SAMPLE_SIZES), 5),
    )

    plt.show()