"""Minimum working example of growbikenet."""

import growbikenet as gbn

a_edges = gbn.growbikenet(
    city_name="Bath",
    proj_crs="3857",
    ranking="betweenness_centrality",
    existing_network_spacing=500,
    export_file_format="gpkg",
    export_data=True,
    export_plots=False,
    export_video=False,
)

# data is saved in current working directory
