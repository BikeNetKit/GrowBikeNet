"""Example of growbikenet used during package development."""

import growbikenet as gbn

gbn.settings.export_file_format = "geojson"
gbn.settings.import_path = "/Users/mszell/Tresorit/bikenetkitshare/"

city_id = "soligorsk_by"

edges_ordered = gbn.growbikenet(
            "Soli",
            existing_network_spacing='auto',
            import_files={
                'growable_network':"growable_networks/"+city_id+".gpkg",
                'bike_network':"bike_networks/"+city_id+".gpkg",
                'seed_points':"rail_stations/"+city_id+".gpkg"
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