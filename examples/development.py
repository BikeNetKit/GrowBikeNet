"""Example of growbikenet used during package development."""

import growbikenet as gbn

# constants.GROWABLE_NETWORK_CUSTOM_FILTER = None
# constants.GROWABLE_NETWORK_TYPE = 'all'


gbn.settings.viz["bike_existing"]["color"] = "#6a6ab8"
gbn.settings.viz["bike_to_grow"]["line_width"] = 0
gbn.settings.viz["seed_point"]["markersize"] = 0
gbn.settings.viz["dpi"] = 600

edges_ordered = gbn.growbikenet("Podgorica", 
    existing_network_spacing = 'auto',
    export_data = True,
    export_plots = True,
    seed_point_linking = 'triangulate_delaunay',
    seed_point_type = 'grid_square',
    import_files={
        # 'city_boundary':"./tests/test_data/copenhagen_city_boundary.shp"
        # 'street_network':"./tests/test_data/podgorica_me_street_network.gpkg",
        # 'bike_network':"./tests/test_data/podgorica_me_bike_network.gpkg",
        # 'point_data':"./tests/test_data/turin_crashes.gpkg",
        # 'trip_data':"./tests/test_data/turin_trips.csv",
        },
    )
# print(edges_ordered.tail())