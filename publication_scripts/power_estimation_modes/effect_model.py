import numpy as np


def draw_true_effects(n_variables, tau_A=1.0, tau_mu=0.5, rng_np=None):
    """Draw the network-level distribution parameters"""

    if rng_np is None:
        rng_np = np.random.default_rng()

    # Draw mean from random effects 
    mu_A = rng_np.normal(loc=0, scale=np.sqrt(tau_mu))
    # Draws overall effects
    A_ = rng_np.normal(loc=mu_A, scale=np.sqrt(tau_A), size=(1, n_variables))

    # broadcast to an ROI x ROI
    iu, ju = np.triu_indices(n_nodes, k=1)
    A_edge = np.zeros((n_nodes, n_nodes))
    A_edge[iu, ju] = A_g
    A_edge[ju, iu] = A_g

    return A_edge


def draw_true_effects(A_edge, c, rng_np=None):

    if rng_np is None:
        rng_np = np.random.default_rng()

    TE = np.zeros_like(A_edge)

    cov_draw = rng_np.normal(scale=1, size=1)[0]
    ind_draw = rng_np.normal(scale=1, size=A_edge.shape)

    for i, j in np.ndindex(A_edge.shape):
        if i > j:
            continue

        TE[i, j] = np.sqrt(c)*cov_draw + np.sqrt(1 - c)*ind_draw[i, j]
        TE[i, j] = A_edge[i, j]*TE[i, j]
        TE[j, i] = TE[i, j]

    return TE


def draw_subject_array(TE, n_subs, tau_S, c, rng_np=None):

    if rng_np is None:
        rng_np = np.random.default_rng()

    iu, ju = np.triu_indices(TE.shape[0], k=1)
    subject_array = np.zeros((n_subs, TE.shape[0], TE.shape[1]))

    for i in range(n_subs):

        # Covariate error and individual error draw
        cov_draw = rng_np.standard_normal()
        ind_draw = rng_np.standard_normal(TE.shape)

        eps = np.sqrt(tau_S) * (np.sqrt(c)*cov_draw + np.sqrt(1 - c)*ind_draw)

        R = TE + eps
        R[ju, iu] = R[iu, ju]
        np.fill_diagonal(R, 0)
        subject_array[i] = R

    return subject_array


def stack_subject_arrays(*subject_arrays):
    return np.concatenate(*subject_arrays, axis=0)


def group_level_effect(subject_array, axis=0):
    return np.mean(subject_array, axis=axis)


def create_draw_distribution_function(TE, c=0.0, rng_np=None):

    iu, ju = np.triu_indices(TE.shape[0], k=1)

    if rng_np is None:
        rng_np = np.random.default_rng()

    def draw(sample_size):

        sd = np.sqrt(1 / sample_size)

        # Common shock - shared subjects - redrawn every call
        cov_draw = rng_np.standard_normal()
        ind_draw = rng_np.standard_normal(TE.shape)

        eps = sd * (np.sqrt(c)*cov_draw + np.sqrt(1 - c)*ind_draw)

        R = TE + eps
        R[ju, iu] = R[iu, ju]
        np.fill_diagonal(R, 0)
        return R

    return draw


if __name__ == '__main__':

    # Draw true effects
    A_edge = draw_distribution_amplitude(5, 1)
    TE = draw_true_effects(A_edge, 0.5)
    sub_draw = draw_subject_array(TE, 3, 0.5, 0.5)
    gl_effect = group_level_effect(sub_draw)
    print(gl_effect)



