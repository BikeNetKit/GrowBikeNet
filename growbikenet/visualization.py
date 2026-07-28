"""Visualization functions for growbikenet."""

from . import constants
from . import settings
import os
import glob
import re
import pathlib
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm


def create_plots(
    edges_ranked, seed_points_snapped, ranking
):

    for ordering in tqdm(
        sorted(list(edges_ranked.index)),
        desc="{:<23}".format("Generating plots"),
        leave=True,
        unit="plot",
        bar_format='{l_bar}{bar:16}{r_bar}',
        ):

        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

        # first, plot street network as "base line"
        edges_ranked.plot(ax=ax, color=settings.viz['color']['street'], lw=settings.viz['line_width']['street'], zorder=0)

        # plot all edges up to current rank

        edges_ranked[edges_ranked.index <= ordering].plot(
            ax=ax, color=settings.viz['color']['edge'], lw=settings.viz['line_width']['bike'], zorder=1
        )

        seed_points_snapped.plot(ax=ax, color=settings.viz['color']['seed_point'], zorder=2)

        ax.set_axis_off()

        plot_id = "{:04d}".format(int(ordering))  # format plot ID with leading zeros

        fig.savefig(settings.export_path['plots']+f"ordering_{ranking}/{plot_id}.png", dpi=settings.viz['dpi'], bbox_inches='tight')

        plt.close()
