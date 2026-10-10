"""Example of growbikenet used during package development."""

import growbikenet as gbn

gbn.settings.export_file_format = "gpkg"
# gbn.settings.import_path = "/Users/mszell/Tresorit/bikenetkitshare/"
gbn.settings.import_path = "./tests/test_data/"

city_id = "badalona_es"

gbn.settings.import_data_impact = 9
gbn.settings.import_data_trip_point_balance = 0.4 # alpha

gbn.growbikenet(
    "Turin", 
    import_files={
        'growable_network':"turin_growable_network.gpkg",
        'point_data':"turin_crashes.gpkg",
        'trip_data':"turin_trips.csv",
    },
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