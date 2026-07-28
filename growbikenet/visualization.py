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


def create_plots(edges_ranked, seed_points_snapped, ranking, with_existing_bike_network):
    """Plot frames of a growing bicycle network 

    Results are png files saved into settings.export_path['plots'].

    Parameters
    ----------
    edges_ranked : geopandas.geodataframe.GeoDataFrame
        Ordered geodataframe of all edges in street network, representing a growing bicycle network
    seed_points_snapped : geopandas.geodataframe.GeoDataFrame
        Set of seed points snapped to the street network, representing the growing bicycle network nodes
    ranking : str
        Method used to rank edges.
    with_existing_bike_network : bool
        Boolean deciding whether the plot is with or without existing bike network.
    """

    for ordering in tqdm(
        list(range(len(edges_ranked)))[:-1] if with_existing_bike_network else list(range(len(edges_ranked)+1)), # An extra frame upfront is used to show the empty net, so we need to add an extra frame in the end.
        desc="{:<23}".format("Generating plots"),
        leave=True,
        unit="plot",
        bar_format='{l_bar}{bar:16}{r_bar}',
        ):

        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

        # Plot to grow network as base line
        edges_ranked.plot(ax=ax, color=settings.viz['bike_to_grow']['color'], lw=settings.viz['bike_to_grow']['line_width'], zorder=0)

        if with_existing_bike_network:
            # Plot existing bike network
            edges_ranked.iloc[[0]].plot(
                ax=ax, color=settings.viz['bike_existing']['color'], lw=settings.viz['bike_existing']['line_width'], zorder=1
            )

        # Plot all edges up to current rank
        if ordering >= 1:
            edges_ranked.iloc[int(with_existing_bike_network):ordering+int(with_existing_bike_network)].plot(
                ax=ax, color=settings.viz['bike_grown']['color'], lw=settings.viz['bike_grown']['line_width'], zorder=1
            )

        seed_points_snapped.plot(ax=ax, color=settings.viz['seed_point']['color'], markersize=settings.viz['seed_point']['markersize'], edgecolor=settings.viz['seed_point']['edgecolor'], zorder=2)

        ax.set_axis_off()

        plot_id = "{:04d}".format(int(ordering))  # format plot ID with leading zeros

        fig.savefig(settings.export_path['plots']+f"ordering_{ranking}/{plot_id}.png", dpi=settings.viz['dpi'], bbox_inches='tight')

        plt.close()
