import numpy as np
import matplotlib.pyplot as plt
from effect_model import (
    draw_distribution_amplitude,
    draw_true_effects,
    create_draw_distribution_function
)


def plot_multiple_experiments(draw_function, K, sample_size):

    panels = np.stack([draw_function(sample_size) for _ in range(K)])
    vmax = np.abs(panels).max()

    ncols = 3
    nrows = int(np.ceil(K / ncols))
    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(4*ncols, 4*nrows),
                             squeeze=False)

    for ax, M, i in zip(axes.ravel(), panels, range(K)):
        im = ax.imshow(M, cmap="RdBu_r", vmin=-vmax, vmax=vmax)
        ax.set_title(f"experiment {i+1}")
        ax.set_xticks([]); ax.set_yticks([])

    for ax in axes.ravel()[K:]:
        ax.axis("off")

    fig.colorbar(im, ax=axes, shrink=0.8)
    fig.suptitle(f"N = {sample_size}")
    plt.show()


if __name__ == '__main__':

    A_edge = draw_distribution_amplitude(seed=0, n_nodes=50, tau_A=1.0)
    TE = draw_true_effects(A_edge, c=0.8)
    draw = create_draw_distribution_function(TE, tau_e=1.0)

    plot_multiple_experiments(draw, K=6, sample_size=100)