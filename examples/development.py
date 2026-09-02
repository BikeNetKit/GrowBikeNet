"""Example of growbikenet used during package development."""

import growbikenet as gbn

gbn.settings.export_file_format = "geojson"
edges_ordered = gbn.growbikenet("Frederiksberg municipality",
                               export_data=True,
                               existing_network_spacing='auto',
                               # import_files={'growable_network':'podgorica_growable_network.gpkg',
                               # 'bike_network':'podgorica_bike_network.gpkg'},
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