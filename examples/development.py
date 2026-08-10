"""Example of growbikenet used during package development."""

import growbikenet as gbn

gbn.settings.import_data_impact = 9
gbn.settings.import_data_trip_point_balance = 0.4 # alpha
gbn.settings.export_file_format = "gpkg"
gbn.settings.crs_result = "3857"
edges_ordered = gbn.growbikenet("Athens", 
    existing_network_spacing = 'auto',
    export_data = True,
    export_plots = True,
    # seed_point_linking = 'quadrangulate',
    # seed_point_type = 'grid_square',
    import_files={
        'street_network':"./tests/test_data/athens_street_network.gpkg",
        'bike_network':"./tests/test_data/athens_bike_network.gpkg",
        # 'point_data':"./tests/test_data/turin_crashes.gpkg",
        # 'trip_data':"./tests/test_data/turin_trips.csv",
        },
    )
# print(edges_ordered.tail())