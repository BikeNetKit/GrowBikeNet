"""Example of growbikenet used during package development."""

import growbikenet as gbn

edges_ranked = gbn.growbikenet("Turin", 
    import_files={
        'street_network':"./tests/test_data/turin_street_network.gpkg",
        'point_data':"./tests/test_data/turin_crashes.gpkg",
        'trip_data':"./tests/test_data/turin_trips.csv",
        },
    )