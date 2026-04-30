"""Minimum working example of growbikenet."""

import growbikenet as gbn

a_edges = gbn.growbikenet(
    city_name="Oelde",
    ranking="betweenness_centrality",
    existing_network_spacing=None,
    export_file_format="gpkg",
    export_data=True,
    export_plots=False,
    export_video=False,
    allow_edge_overlaps=False,
)

# data is saved in current working directory
