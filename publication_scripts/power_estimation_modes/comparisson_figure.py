import numpy as np
import matplotlib.pyplot as plt

from study_planning_strats import (
    estimate_power_strongest_effect,
    estimate_power_average_significant_effect,
    estimate_power_average_effect,
    estimate_power_subsampling_repetition,
    estimate_true_power
)

from effect_model import (
    draw_true_effects,
    draw_subject_array
)

# Set seed for effect model and draw true effects
# Only one set of true effects is fine for now
SEED = 20260724
rng_np = np.random.default_rng()
N_NODES = 55
N_VARIABLES = N_NODES*(N_NODES - 1)//2  # Not really a constant but fine
TAU_A = 1.0
TAU_S = 1.0
TAU_MU = 0

# Sample size - 40 subjects - idea scale
SAMPLE_SIZE = 40

# For K values 10, 20, 50, 100, 200 - number of winners curse predictors
K_VALUES = (10, 20, 50, 100, 200)

# Estimator strategy lists (subsampling repetition handled separately below,
# since it takes a pooled-subject array rather than a stacked-experiment array)
ESTIMATORS = [
    estimate_power_strongest_effect,
    estimate_power_average_significant_effect,
    estimate_power_average_effect,
    estimate_power_subsampling_repetition
]

LABELS = ('strongest effect', 'average significant', 'average effect',
          'subsampling repetition')


# Draw true effects
TE = draw_true_effects(
    n_variables=N_VARIABLES,
    tau_A=TAU_A,
    rng_np=rng_np
)


def draw():
    return draw_subject_array(
        TE=TE,
        n_subs=SAMPLE_SIZE,
        tau_S=TAU_S,
        tau_mu=TAU_MU,
        rng_np=rng_np
    )


# Create stack of experiments: (max(K_VALUES), SAMPLE_SIZE, N_VARIABLES)
stack_full = np.stack([draw() for _ in range(max(K_VALUES))])

# Results array: one row per estimator (incl. subsampling), one col per K
results = np.zeros((len(LABELS), len(K_VALUES)))

for k_idx, K in enumerate(K_VALUES):

    for e_idx, estimator in enumerate(ESTIMATORS):
        results[e_idx, k_idx] = estimator(
            stack_full, N_VARIABLES, SAMPLE_SIZE, K
        )

# Calculate true power using real effects
true_power = estimate_true_power(
    TE,
    N_VARIABLES,
    SAMPLE_SIZE
)

# Plot results - one figure per estimator, each against true power
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
axes = axes.ravel()

for ax, label, row in zip(axes, LABELS, results):
    ax.plot(K_VALUES, row, marker='o', color='tab:blue', label=label)
    ax.axhline(true_power, color='k', ls='--', label='true power')

    ax.set_xscale('log')
    ax.set_xticks(K_VALUES)
    ax.set_xticklabels(K_VALUES)
    ax.set_xlabel('K (winners curse draws)')
    ax.set_ylabel(f'power at N = {SAMPLE_SIZE}')
    ax.set_title(label)
    ax.set_ylim(0, 1.02)
    ax.legend(frameon=False)

fig.tight_layout()
plt.show()
