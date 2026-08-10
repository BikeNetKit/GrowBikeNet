"""Example of growbikenet used during package development."""

import growbikenet as gbn

gbn.settings.import_data_impact = 9
gbn.settings.import_data_trip_point_balance = 0.4 # alpha
gbn.settings.export_file_format = "geojson"
gbn.settings.crs_result = "4326"
edges_ordered = gbn.growbikenet("Turin", 
    export_data = True,
    import_files={
        'street_network':"./tests/test_data/turin_street_network.gpkg",
        'point_data':"./tests/test_data/turin_crashes.gpkg",
        'trip_data':"./tests/test_data/turin_trips.csv",
        },
    )
print(edges_ordered.tail())