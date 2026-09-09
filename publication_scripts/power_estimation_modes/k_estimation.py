from effect_model import (
    draw_true_effects,
    draw_experiment_array,
)
from utils import(
    edges_to_pvalues_from_experiment,
    significance_map
)
from joblib import( 
    Parallel,
    delayed
)
import numpy as np


def run_any_significant_test(
    seed,
    p_crit,
    n_subs,
    n_variables,
    tau_A,
    tau_S,
    max_K,
):
    rng_np = np.random.default_rng(seed)

    true_effects = draw_true_effects(
            n_variables=n_variables,
            tau_A=tau_A,
            tau_S=tau_S,
            rng_np=rng_np
        )

    K = 0

    while True and K < max_K:

        experiment_effects = draw_experiment_array(
            TE=true_effects,
            n_subs=n_subs,
            tau_mu=0,
            rng_np=rng_np
        )

        p_value_array = edges_to_pvalues_from_experiment(
            E=experiment_effects,
            N=n_subs
        )

        sig_array = significance_map(
            p_value_array,
            n_variables=n_variables,
            alpha=p_crit
        )

        K += 1

        if np.any(sig_array):
            break

    if K >= max_K:
        print('Max K reached')

    return K


if __name__ == '__main__':

    # VALUES BEING ANALYZED
    P_CRIT = [0.10, 0.05, 0.01, 0.005]
    N_SUBS = 160

    # CONSTANT SETTING
    N_NODES = 268
    N_VARIABLES = N_NODES * (N_NODES - 1) // 2
    TAU_A = 0.00088
    TAU_S = 1.0
    TAU_MU = 0
    MAX_K = 100000
    N_MAJOR_REPS = 100
    JOB_NUMBER = 5

    results_dict = {}
    for p_c in P_CRIT:

        seeds = [i for i in range(N_MAJOR_REPS)]

        results = Parallel(
            n_jobs=JOB_NUMBER,
            backend="loky",
        )(delayed(run_any_significant_test)(
            seed=seed,
            p_crit=p_c,
            n_subs=N_SUBS,
            n_variables=N_VARIABLES,
            tau_A=TAU_A,
            tau_S=TAU_S,
            max_K=MAX_K,
        ) for seed in seeds)

        results = np.array(results)
        K_mean = results.mean()
        print(f'For {p_c} the estimated K value is {K_mean}')
        results_dict[p_c] = K_mean

    print("Final results")
    for key, value in results_dict.items():
        print(f"{key}: {value}")

