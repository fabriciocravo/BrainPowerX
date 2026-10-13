import numpy as np
from joblib import Parallel, delayed

from utils import calculate_power_fwer
from true_effect_models import normal_true_effects


def compute_avg_power(
        TE_model,
        sample_sizes,
        n_variables,
        quantiles,
        seed=None
):
    """
    True average power of the top-q fraction of effects, per sample size,
    for a single draw of the true effects.

    Returns an array of shape (n_quantiles, n_sample_sizes).
    """
    rng_np = np.random.default_rng(seed)

    TE = np.abs(TE_model(n_variables, rng_np))
    order = np.argsort(TE)

    power_table = np.zeros((len(quantiles), len(sample_sizes)))

    for i_s, n_sample in enumerate(sample_sizes):

        # Per-variable true power, computed once per sample size
        true_power = calculate_power_fwer(
            TE,
            n_variables,
            n_sample
        )
        # Sort power by effect size (ascending), so the top-q slice
        # matches the top-q effects
        true_power = true_power[order]

        for i_q, q in enumerate(quantiles):
            nq_var = int(round(q*n_variables))
            power_table[i_q, i_s] = true_power[-nq_var:].mean()

    return power_table


def print_table(power_table, quantiles, n_effects, sample_sizes, tau_A):
    label_w = 26
    col_w = 12

    print(f"\nTrue average power (FWER), tau_A = {tau_A:g}")
    print("Rows: top-quantile of effects; columns: sample size\n")

    header = "Quantile (n effects)".ljust(label_w)
    header += "".join(f"N={n}".rjust(col_w) for n in sample_sizes)
    print(header)
    print("-" * len(header))

    for i_q, q in enumerate(quantiles):
        label = f"{q:.3g} ({n_effects[i_q]})".ljust(label_w)
        row = "".join(f"{p:.4f}".rjust(col_w) for p in power_table[i_q])
        print(label + row)
    print()


if __name__ == '__main__':

    N_NODES = 268
    N_VARIABLES = N_NODES * (N_NODES - 1) // 2

    QUANTILES = [0.01, 0.1, 0.3, 0.5, 1]
    SAMPLE_SIZES = [40, 80, 120]

    TAU_A = 0.025
    TAU_S = 1.0

    N_REPS = 5000
    N_JOBS = 10

    def TE_normal(n_var, rng):
        return normal_true_effects(
            n_variables=n_var,
            tau_A=TAU_A,
            tau_S=TAU_S,
            rng_np=rng
        )

    # Number of effects per quantile (for the table labels)
    n_effects_list = [
        int(round(q * N_VARIABLES)) for q in QUANTILES
    ]

    # Shape: (n_quantiles, n_sample_sizes)
    power_mean = np.zeros((len(QUANTILES), len(SAMPLE_SIZES)))

    outputs = Parallel(n_jobs=N_JOBS, verbose=5)(
        delayed(compute_avg_power)(
            TE_model=TE_normal,
            sample_sizes=SAMPLE_SIZES,
            n_variables=N_VARIABLES,
            quantiles=QUANTILES,
            seed=None,
        )
        for _ in range(N_REPS)
    )

    for power_table in outputs:
        power_mean += power_table

    power_mean = power_mean / N_REPS

    print_table(power_mean, QUANTILES, n_effects_list, SAMPLE_SIZES, TAU_A)

    