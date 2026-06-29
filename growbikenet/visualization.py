from growbikenet.constants import *
from . import settings
import os
import glob
import re
import pathlib
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm


def create_plots(
    routed_edges_gdf, seed_points_snapped, streetcolor, edgecolor, seedcolor, lws, ranking
):

    for ordering in tqdm(
        sorted(routed_edges_gdf["ordering_"+ranking].unique()),
        desc="{:<23}".format("Generating plots"),
        leave=True,
        unit="plot",
        bar_format='{l_bar}{bar:16}{r_bar}',
        ):

        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

        # first, plot street network as "base line"
        routed_edges_gdf.plot(ax=ax, color=streetcolor, lw=lws["street"], zorder=0)

        # plot all edges up to current rank

        routed_edges_gdf[routed_edges_gdf["ordering_"+ranking] <= ordering].plot(
            ax=ax, color=edgecolor, lw=lws["bike"], zorder=1
        )

        seed_points_snapped.plot(ax=ax, color=seedcolor, zorder=2)

        ax.set_axis_off()

        plot_id = "{:03d}".format(int(ordering))  # format plot ID with leading zeros

        fig.savefig(settings.export_path['plots']+f"ordering_{ranking}/{plot_id}.png", dpi=150, bbox_inches='tight')

        plt.close()
