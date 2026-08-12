"""Example of growbikenet used during package development."""

import growbikenet as gbn
from growbikenet import constants

# constants.GROWABLE_NETWORK_CUSTOM_FILTER = None
# constants.GROWABLE_NETWORK_TYPE = 'all'

edges_ordered = gbn.growbikenet("Podgorica", 
    existing_network_spacing = 'auto',
    export_data = True,
    export_plots = True,
    seed_point_linking = 'triangulate_delaunay',
    seed_point_type = 'grid_square',
    import_files={
        # 'street_network':"./tests/test_data/podgorica_me_street_network.gpkg",
        # 'bike_network':"./tests/test_data/podgorica_me_bike_network.gpkg",
        # 'point_data':"./tests/test_data/turin_crashes.gpkg",
        # 'trip_data':"./tests/test_data/turin_trips.csv",
        },
    )
# print(edges_ordered.tail())