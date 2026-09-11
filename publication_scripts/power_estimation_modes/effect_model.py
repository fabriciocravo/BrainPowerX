import numpy as np


def draw_true_effects(n_variables, tau_A=1.0, tau_S=1.0, rng_np=None):
    """Draw the network-level distribution parameters"""

    if rng_np is None:
        rng_np = np.random.default_rng()

    # Draws overall effects
    TE = rng_np.normal(
        loc=0,
        scale=np.sqrt(tau_A),
        size=n_variables
    )/np.sqrt(tau_S)  # Scaling to units of noise

    return TE


def draw_subject_array(TE, n_subs, tau_mu, rng_np=None):

    if rng_np is None:
        rng_np = np.random.default_rng()

    # Introduce a small bias to every experiment
    TE_b = TE + rng_np.normal(loc=0, scale=np.sqrt(tau_mu))

    subject_array = np.zeros((n_subs, *TE.shape))

    for i in range(n_subs):

        ind_draw = rng_np.normal(loc=0, scale=1, size=TE.shape)

        R = TE_b + ind_draw
        subject_array[i] = R

    return subject_array


def draw_experiment_array(TE, n_subs, tau_mu, rng_np=None):

    if rng_np is None:
        rng_np = np.random.default_rng()

    # Introduce a small bias to every experiment
    TE_b = TE + rng_np.normal(loc=0, scale=np.sqrt(tau_mu))

    E = TE_b + rng_np.normal(
        loc=0,
        scale=1/np.sqrt(n_subs),
        size=TE.shape
    )
    
    return E


def draw_t_array_sub_level(seed_list, TE, n_subs, tau_mu):

    rng_np = np.random.default_rng()
    TE_b = TE + rng_np.normal(loc=0, scale=np.sqrt(tau_mu))

    if len(seed_list) != n_subs:
        raise TypeError(
            'Function draw_experiment_array_sub_level'
            'requires seeds equal to number of subjects'
        )

    mean = 0
    M2 = 0
    for i, seed in enumerate(seed_list):
        rng_np = np.random.default_rng(seed)

        x = rng_np.normal(loc=0, scale=1, size=TE.shape)
        delta = x - mean
        mean += delta/(i + 1)
        delta_2 = x - mean
        M2 += delta*delta_2

    variance = M2/n_subs
    mean_variance = variance / n_subs
    
    standardized_mean = mean / np.sqrt(mean_variance)

    experiment_effects = TE_b + standardized_mean

    return experiment_effects



def draw_experiement_variance(TE, n_subs, rng_np=None):

    if rng_np is None:
        rng_np = np.random.default_rng()

    # The variance is a chi_squared dist
    exp_variance = rng_np.chisquare(n_subs - 1, size=TE.shape) / (n_subs - 1)
    return exp_variance



def stack_subject_arrays(*subject_arrays):
    return np.concatenate(*subject_arrays, axis=0)


def group_level_effect(subject_array, axis=0):
    return np.mean(subject_array, axis=axis)


if __name__ == '__main__':

    # Draw true effects
    TE = draw_true_effects(1485, 0.5)
    sub_draw = draw_subject_array(TE, 3, 0.5)
    gl_effect = group_level_effect(sub_draw)
    print(gl_effect)
    print(gl_effect.shape)
    print(sub_draw.shape)



