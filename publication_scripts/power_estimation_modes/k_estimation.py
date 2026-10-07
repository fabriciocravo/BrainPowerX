from significance_planning_strats import (
    first_significant_experiment
)
from true_effect_models import(
    normal_true_effects
)
from joblib import( 
    Parallel,
    delayed
)
import numpy as np


def run_any_significant_test(
    TE_model,
    n_variables,
    n_sample,
    p_crit,
    seed=None
):
    
    if seed is not None:
        rng_np = np.random.default_rng(seed)
    else:
        rng_np = np.random.default_rng()

    TE = TE_model(n_variables, rng=rng_np)

    _, _, K = first_significant_experiment(
        TE,
        n_variables=n_variables,
        sample_size=n_sample,
        alpha=p_crit,
        max_sig_iteration=10000
    )
       
    return K


if __name__ == '__main__':

    # VALUES BEING ANALYZED
    P_CRIT = [0.10, 0.05, 0.01, 0.005]
    N_SUBS_LIST = [10, 20, 40, 80, 120]
    N_REPS = 10000

    # CONSTANT SETTING
    N_NODES = 268
    N_VARIABLES = N_NODES * (N_NODES - 1) // 2

    # Normal Model
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

    #################
    JOB_NUMBER = 10

    results_dict = {}
    for n_sub in N_SUBS_LIST:
        for p_c in P_CRIT:

            results = Parallel(
                n_jobs=JOB_NUMBER,
                backend="loky",
            )(delayed(run_any_significant_test)(
                TE_model=TE_normal,
                n_variables=N_VARIABLES,
                seed=seed,
                p_crit=p_c,
                n_sample=n_sub,
            ) for seed in range(N_REPS))

            results = np.array(results)
            K_mean = results.mean()
            print(f'For {p_c} and {n_sub} the estimated K value is {K_mean}')
            results_dict[(n_sub, p_c)] = K_mean

    print("Final results")
    for key, value in results_dict.items():
        print(f"{key}: {value}")

