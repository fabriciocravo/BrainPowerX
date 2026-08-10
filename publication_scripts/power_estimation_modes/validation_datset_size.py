import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

from effect_model import (
    draw_true_effects,
    draw_subject_array
)

from study_planning_strats import (
    estimate_power_subsampling_repetition,
    estimate_true_power
)

N_NODES = 30
N_VARIABLES = N_NODES * (N_NODES - 1) // 2
TAU_A = 0.00088
TAU_S = 1.0
TAU_MU = 0
REP_NUMBER = 500
SAMPLE_SIZE = 10
DATASET_SIZES = [2, 4, 8]


def run_one_repetition(
    i_d_ds_pairs,
    N_VARIABLES,
    SAMPLE_SIZE,
    TAU_A,
    TAU_S,
    TAU_MU,
    seed=None
):
    rng_np = np.random.default_rng(seed)

    # Draw true effects
    TE = draw_true_effects(
        n_variables=N_VARIABLES,
        tau_A=TAU_A,
        rng_np=rng_np
    )

    # Deterministic given TE and n_sample -> compute once
    tp = estimate_true_power(
        TE,
        N_VARIABLES,
        SAMPLE_SIZE,
        return_full_matrix=True
    )

    n_ds = len(i_d_ds_pairs)
    p_diff = np.zeros(n_ds)
    max_p_diff = np.zeros(n_ds)

    for i_d, ds in i_d_ds_pairs:
        n_subs = int(ds * SAMPLE_SIZE)

        dataset = np.asarray([draw_subject_array(
            TE=TE,
            n_subs=n_subs,
            tau_S=TAU_S,
            tau_mu=TAU_MU,
            rng_np=rng_np
        )])

        power = estimate_power_subsampling_repetition(
            dataset,
            N_VARIABLES,
            SAMPLE_SIZE,
            exp_number=1,
            return_full_matrix=True,
            rng_np=rng_np
        )

        p_diff[i_d] = np.abs(np.mean(power) - np.mean(tp))
        max_p_diff[i_d] = np.abs((power - tp).max())

    return tp, p_diff, max_p_diff


# --- driver ---
i_d_ds_pairs = list(enumerate(DATASET_SIZES))

results = Parallel(n_jobs=5)(
    delayed(run_one_repetition)(
        i_d_ds_pairs, N_VARIABLES, SAMPLE_SIZE, TAU_A, TAU_S, TAU_MU, seed=i_r
    )
    for i_r in range(REP_NUMBER)
)

# Unpack results back into the original arrays
# (REP_NUMBER, N_VARIABLES)
true_power = np.array([r[0] for r in results])
# (REP_NUMBER, len(DATASET_SIZES))
power_diff = np.array([r[1] for r in results])
# (REP_NUMBER, len(DATASET_SIZES))
max_power_diff = np.array([r[2] for r in results])

mean_over_reps = power_diff.mean(axis=0)
max_over_reps = max_power_diff.mean(axis=0)

n_samples = [int(ds * SAMPLE_SIZE) for ds in DATASET_SIZES]

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(n_samples, mean_over_reps, marker='o', label='Mean per-edge error')
ax.plot(n_samples, max_over_reps, marker='o', label='Max per-edge error')
ax.axhline(0, color='gray', linestyle='--', linewidth=1)
ax.set_xlabel('Sample size (N)')
ax.set_ylabel('|Estimated power − true power|')
ax.set_title('Bias of subsampling-repetition power estimator')
ax.legend()
plt.tight_layout()
plt.show()
