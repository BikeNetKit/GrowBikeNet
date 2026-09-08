"""Example of growbikenet used during package development."""

import growbikenet as gbn


gbn.settings.export_file_format = "gpkg"

# edges_ordered = gbn.growbikenet("Municipality of Athens",
#                                export_data=True,
#                                existing_network_spacing='auto',
#                                # import_files={'growable_network':'podgorica_growable_network.gpkg',
#                                # 'bike_network':'podgorica_bike_network.gpkg'},
#                                export_plots=True,
#                                )

gbn.settings.import_data_impact = 9
gbn.settings.reroute = False
gbn.settings.viz['seed_point']['markersize'] = 0
edges_ordered_with_crashes = gbn.growbikenet(
    "Turin",
    import_files = {
        'growable_network': 'turin_it.gpkg',
        'point_data': 'turin_crashes.gpkg',
    },
    seed_point_linking = 'triangulate_delaunay',
    export_plots=True,
)

# import osmnx as ox
# import networkx as nx

# g = ox.graph_from_place("Podgorica", 
#     custom_filter=gbn.constants.GROWABLE_NETWORK_CUSTOM_FILTER)
# g = nx.MultiGraph(ox.convert.to_digraph(g))
# ox.io.save_graph_geopackage(g, "podgorica_growable_network.gpkg")

# g = ox.graph_from_place(
#     "Podgorica",
#     custom_filter=gbn.constants.PBI_CUSTOM_FILTER,
#     retain_all=True, # fetch all connected components
# )
# g = nx.MultiGraph(ox.convert.to_digraph(g))
# ox.io.save_graph_geopackage(g, "podgorica_bike_network.gpkg")