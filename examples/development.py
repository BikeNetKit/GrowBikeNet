"""Example of growbikenet used during package development."""

import growbikenet as gbn

# import osmnx as ox
# import networkx as nx
# file_out = "asti_graph.gpkg"
# city_boundary_gdf = ox.geocoder.geocode_to_gdf("Asti 16")
# city_boundary_geometry = city_boundary_gdf.geometry[0]
# G = ox.graph_from_polygon(city_boundary_geometry, network_type="drive")
# G = ox.convert.to_digraph(G)
# G = nx.MultiGraph(G)
# ox.io.save_graph_geopackage(G, file_out)

gbn.settings.export_file_format = 'gpkg'
edges_ranked = gbn.growbikenet("Asti 16",
    import_files={"street_network": "./tests/test_data/asti_street_network.gpkg"})