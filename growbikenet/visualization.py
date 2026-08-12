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


def generate_plots(edges_ordered, nodes, ordering, with_existing_bike_network):
    """Plot frames of a growing bicycle network 

    Results are png files saved into settings.export_path['plots'].

    Parameters
    ----------
    edges_ordered : geopandas.geodataframe.GeoDataFrame
        Ordered geodataframe of all edges in street network, representing a growing bicycle network
    nodes : geopandas.geodataframe.GeoDataFrame
        Set of seed points snapped to the street network, representing the growing bicycle network nodes
    ordering : str
        Method used to order edges.
    with_existing_bike_network : bool
        Boolean deciding whether the plot is with or without existing bike network.

    Returns
    -------
    figs : list
        List of figure handles
    """

    # Set plot CRS
    edges_ordered.to_crs(settings.viz["crs"], inplace=True)
    nodes.to_crs(settings.viz["crs"], inplace=True)

    # Loop through frames
    n = len(edges_ordered)+int(not with_existing_bike_network)
    figs = [0]*n

    for framenum in tqdm(
        list(range(n)), # An extra frame upfront is used to show the empty net, so we need to add an extra frame in the end.
        desc="{:<23}".format("Generating plots"),
        leave=True,
        unit="plot",
        bar_format='{l_bar}{bar:16}{r_bar}',
        ):

        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_axes([0, 0, 1, 1])

        # Plot to grow network as base line
        edges_ordered.plot(ax=ax, color=settings.viz['bike_to_grow']['color'], lw=settings.viz['bike_to_grow']['line_width'], zorder=0)

        if with_existing_bike_network:
            # Plot existing bike network
            edges_ordered.iloc[[0]].plot(
                ax=ax, color=settings.viz['bike_existing']['color'], lw=settings.viz['bike_existing']['line_width'], zorder=1
            )

        # Plot all edges up to current framenum
        if framenum >= 1:
            edges_ordered.iloc[int(with_existing_bike_network):framenum+int(with_existing_bike_network)].plot(
                ax=ax, color=settings.viz['bike_grown']['color'], lw=settings.viz['bike_grown']['line_width'], zorder=1
            )

        nodes.plot(ax=ax, color=settings.viz['seed_point']['color'], markersize=settings.viz['seed_point']['markersize'], edgecolor=settings.viz['seed_point']['edgecolor'], zorder=2)

        ax.set_axis_off()

        plot_id = "{:04d}".format(framenum)  # format plot ID with leading zeros

        fig.savefig(settings.export_path['plots']+f"ordering_{ordering}/{plot_id}.png", dpi=settings.viz['dpi'])
        figs[framenum] = fig
        plt.close()
        
    return figs
